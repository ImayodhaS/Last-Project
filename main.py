import pygame
import random
import sys
import asyncio

pygame.init()
pygame.mixer.init()

W = 900
H = 600

layar = pygame.display.set_mode((W,H))
pygame.display.set_caption("Pemilahan Sampah")

FPS = 60
clock = pygame.time.Clock()

PUTIH = (255, 255, 255)
HITAM = (0, 0, 0)
MERAH = (220, 0, 0)
HIJAU = (0, 180, 0)
BIRUMUDA= (52, 164, 235)

font = pygame.font.Font(None, 40)
font_besar = pygame.font.Font(None, 80)

sound_benar = pygame.mixer.Sound("sfx/benar.wav")
sound_salah = pygame.mixer.Sound("sfx/salah.wav")
sound_gameover = pygame.mixer.Sound("sfx/gameover.wav")

sound_benar.set_volume(0.5)
sound_salah.set_volume(0.5)
sound_gameover.set_volume(0.4)

pygame.mixer.music.load("sfx/backsound.wav")
pygame.mixer.music.set_volume(0.4)

def load_img(nama, scale=1):
    img = pygame.image.load(nama)
    w, h = img.get_size()
    return pygame.transform.scale(img, (int(w*scale), int(h*scale)))

sampah_gambar = {
    "organik": load_img("img/organik.png", 2),
    "anorganik": load_img("img/anorganik.png", 1.5),
    "b3": load_img("img/b3.png", 1.5),
}

tong_gambar = {
    "organik": load_img("img/tong_organik.png", 0.4),
    "anorganik": load_img("img/tong_anorganik.png", 0.4),
    "b3": load_img("img/tong_b3.png", 0.4),
}

class Sampah(pygame.sprite.Sprite):
    def __init__(self, tipe):
        super().__init__()
        self.tipe = tipe
        self.image = sampah_gambar[tipe]
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, max(0,W - self.rect.width))
        self.rect.y = -50
        self.kecepatan = random.randint(2, 4)

    def update(self):
        self.rect.y += self.kecepatan

class Tong(pygame.sprite.Sprite):
    def __init__(self, tipe, x):
        super().__init__()
        self.tipe = tipe
        self.image = tong_gambar[tipe]
        self.rect = self.image.get_rect(center=(x, H - 100))

async def main():
    skor = 0
    hati = 5

    pygame.mixer.music.play(-1)

    sampah_group = pygame.sprite.Group()
    tong_group = pygame.sprite.Group()

    tong_group.add(
        Tong("organik", W//6),
        Tong('anorganik', W//2),
        Tong('b3', W*5//6)
    )

    SPAWN = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN, 1500)

    pegang = None
    offset_x = offset_y = 0
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            
            if hati <= 0:
                pygame.mixer.music.stop()
                # sound_gameover.play()
                await game_over(skor)
                skor = 0
                hati = 5
                return

            if event.type == SPAWN:
                tipe = random.choice(["organik", "anorganik", "b3"])
                sampah_group.add(Sampah(tipe))
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for s in reversed(sampah_group.sprites()):
                        if s.rect.collidepoint(event.pos):
                            pegang = s
                            mx, my = event.pos
                            offset_x = s.rect.x - mx
                            offset_y = s.rect.y - my
                            break

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and pegang:
                    berhasil = False
                    for tong in tong_group:
                        if pegang.rect.colliderect(tong.rect):
                            if pegang.tipe == tong.tipe:
                                sound_benar.play()
                                skor += 10
                            else:
                                sound_salah.play()
                                hati -= 1
                            pegang.kill()
                            berhasil = True
                            break

                    if not berhasil:
                        pegang = None

                    pegang = None

            if event.type == pygame.MOUSEMOTION and pegang:
                mx, my = event.pos
                pegang.rect.x = mx + offset_x
                pegang.rect.y = my + offset_y

            

            for s in sampah_group:
                if s != pegang:
                    if s.rect.y > H:
                        sound_salah.play()
                        hati -= 1
                        s.kill()
        
        layar.fill(BIRUMUDA)
        sampah_group.update()
        tong_group.draw(layar)
        sampah_group.draw(layar)

        teks_skor = font.render(f"Skor: {skor}", True, HITAM)
        teks_nyawa = font.render(f"Nyawa: {hati}", True, HITAM)

        layar.blit(teks_skor, (20, 20))
        layar.blit(teks_nyawa, (W - 150, 20))
        

        pygame.display.update()
        clock.tick(FPS)
        await asyncio.sleep(0)


async def game_over(skor):
    while True:
        layar.fill(HITAM)
        t1 = font_besar.render("GAME OVER", True, MERAH)
        t2 = font.render(f"Skor Kamu: {skor}", True, PUTIH)
        t3 = font.render("Tekan R untuk Restart", True, PUTIH)

        layar.blit(t1, (W//2 - t1.get_width()//2, 150))
        layar.blit(t2, (W//2 - t2.get_width()//2, 300))
        layar.blit(t3, (W//2 - t3.get_width()//2, 400))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    sound_gameover.stop()
                    await main()
                    return
                    
        
        await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(main())

