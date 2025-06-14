##########################################################
####        N A V I O    C A T A    M O E D A S       ####
##########################################################
#### Prof. Filipo Novo Mor - filipomor.com            ####
#### github.com/ProfessorFilipo                       ####
##########################################################
import pygame
import random
import sys

pygame.init()

#  carrega os sons
som_aviso = pygame.mixer.Sound(r'Assets/Audio/notificacao.mp3') #trocar por latido
som_beep = pygame.mixer.Sound(r'Assets/Audio/beep.mp3')

# Carregar a música de fundo
pygame.mixer.music.load(r'Assets/Audio/musicafundo.mp3')  # Caminho da música
pygame.mixer.music.set_volume(0.5)  # Opcional: ajuste o volume entre 0.0 e 1.0
pygame.mixer.music.play(-1, 0.0)  # Toca a música em loop (o '-1' significa loop infinito)

#
# Configurações iniciais
#
WIDTH, HEIGHT = 1366, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Navio Cata Moedas!!!")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont(None, 36)
MOEDA_TAMANHO = (30, 30)

# Carregar a imagem do fundo (altere o caminho para sua imagem real)
background_img = pygame.image.load(r'Assets/PNG/castelo.png').convert()

#porto
# Casinha (porto)
casinha_img = pygame.image.load(r'Assets/PNG/casinha.png').convert_alpha()
casinha_img = pygame.transform.smoothscale(casinha_img, (300, 300))  # Tamanho ajustável
casinha_rect = casinha_img.get_rect(bottomright=(WIDTH - 10, HEIGHT - 0))
#acrescento a imagem
#posição .left = largura da tela - largura do sprite get_width

# barco
barco_sprite_img = pygame.image.load(r'Assets/PNG/cachorrinha.png').convert_alpha()
# Opcionalmente, ajuste o tamanho do sprite
barco_sprite_img = pygame.transform.smoothscale(barco_sprite_img, (360, 180))

#mar
sea_sprite = pygame.image.load(r'Assets/PNG/mar001.png').convert()
sea_sprite = pygame.transform.smoothscale(sea_sprite, (WIDTH, sea_sprite.get_height()))
sea_rect = sea_sprite.get_rect(topleft=(0, HEIGHT - sea_sprite.get_height()))

#
# Função para configurar a dificuldade
#
def configurar_dificuldade(nivel):
    if nivel == 1:
        qtd_moedas = 15
        v_min = 2
        v_max = 3
    elif nivel == 2:
        qtd_moedas = 25
        v_min = 3
        v_max = 4
    elif nivel == 3:
        qtd_moedas = 35
        v_min = 4
        v_max = 6
    elif nivel == 4:
        qtd_moedas = 45
        v_min = 6
        v_max = 8
    else:
        qtd_moedas = 15
        v_min = 2
        v_max = 3
    return qtd_moedas, v_min, v_max

def load_animation_frames(prefix, total_frames=10, tamanho=MOEDA_TAMANHO):
    frames = []
    for i in range(1, total_frames + 1):
        filename = f'{prefix}_{i}.png'
        image = pygame.image.load(filename).convert_alpha()
        image = pygame.transform.smoothscale(image, tamanho)
        frames.append(image)
    return frames

# Carregar sprites das moedas (alterar caminhos conforme seus arquivos)
ouro_frames   = load_animation_frames(r"Assets\PNG\Gold\Gold")
prata_frames  = load_animation_frames(r"Assets\PNG\Silver\Silver")
bronze_frames = load_animation_frames(r"Assets\PNG\Bronze\Bronze")
VALOR_MOEDAS  = {'ouro': 10, 'prata': 5, 'bronze': 1}

# Classe das moedas animadas
class Moeda(pygame.sprite.Sprite):
    def __init__(self, x, y, tipo):
        super().__init__()
        self.tipo = tipo
        self.frames = {
            'ouro': ouro_frames,
            'prata': prata_frames,
            'bronze': bronze_frames
        }[tipo]
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = random.uniform(2, 5)
        self.animation_speed = 0.2
        self.frame_counter = 0

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.x = random.randint(0, WIDTH - self.rect.width)
            self.rect.y = random.randint(-50, -10)
            self.speed = random.uniform(2, 5)
        # Animação
        self.frame_counter += self.animation_speed
        if self.frame_counter >= 1:
            self.frame_counter = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]

# Classe do barco
class Barco(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = barco_sprite_img  # sprite carregado
        self.rect = self.image.get_rect(midbottom=(WIDTH//2, HEIGHT - 20))
        self.speed = 8
        self.carga = 0
        self.max_carga = 100

    def update(self, keys_pressed):
        if keys_pressed[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys_pressed[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

    def voltar_ao_porto(self):
        self.rect.midbottom = (WIDTH // 2, HEIGHT - 20)
        self.carga = 0


#
# Variáveis de controle
#
nivel = 1
qtd_moedas, v_min, v_max = configurar_dificuldade(nivel)
moedas = pygame.sprite.Group()
em_descarga = False
tempo_descarga = 0
pontos = 0

# Criar moedas iniciais
for _ in range(qtd_moedas):
    tipo = random.choice(['ouro', 'prata', 'bronze'])
    x = random.randint(0, WIDTH - 20)
    y = random.randint(-100, -10)
    moedas.add(Moeda(x, y, tipo))

# Instanciar o barco
barco = Barco()

#
# Loop principal do jogo
#
running = True
while running:
    clock.tick(60)  # 60 frames por segundo

    # Processar eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    # Se o barco estiver carregando até o limite, inicia o descarregamento
    if not em_descarga and barco.carga >= barco.max_carga:
        som_aviso.play()

        # Cria uma lista das moedas no céu (fora do alcance do barco)
        moedas_no_ceu = [m for m in moedas if m.rect.y < HEIGHT / 2]
        while moedas_no_ceu:
            moeda_remover = moedas_no_ceu.pop()
            moedas.remove(moeda_remover)

            # Conta 1 ponto negativo por moeda removida
            pontos -= 1
            if pontos < 0:
                pontos = 0

        em_descarga = True
        tempo_descarga = pygame.time.get_ticks()

    if em_descarga:
        # O barco volta ao porto para descarregar
        barco.voltar_ao_porto()
        # Aguarda 2 segundos para descarregar
        if pygame.time.get_ticks() - tempo_descarga > 2000:
            barco.carga = 0
            em_descarga = False
            #ocultar o porto
        continue  # pula o restante do loop enquanto descarrega

    # Atualiza movimento do barco
    barco.update(keys)

    # Atualiza as moedas
    moedas.update()

    # Detecta colisões entre o barco e as moedas
    colisoes = pygame.sprite.spritecollide(barco, moedas, True)
    for moeda in colisoes:
        barco.carga += VALOR_MOEDAS[moeda.tipo]
        som_beep.play()
        pontos += 1
        # Após capturar uma moeda, cria uma nova
        '''tipo_random = random.choice(['ouro', 'prata', 'bronze'])
        x = random.randint(0, WIDTH - 20)
        y = random.randint(-50, -10)
        moedas.add(Moeda(x, y, tipo_random)) '''


    # Garantir que o número de moedas esteja constante
    while len(moedas) < qtd_moedas:
        tipo = random.choice(['ouro', 'prata', 'bronze'])
        x = random.randint(0, WIDTH - 20)
        y = random.randint(-100, -10)
        moedas.add(Moeda(x, y, tipo))

    #
    # Desenhar a tela
    #
    #
    # Desenhar a tela
    #
    screen.blit(sea_sprite, sea_rect)  # Desenha o mar primeiro
    screen.blit(background_img, (0, 0))  # Depois desenha o fundo (castelo)
    screen.blit(casinha_img, casinha_rect)
    score_text = f"Pontos: {pontos}"
    score_surface = FONT.render(score_text, True, (255, 255, 255))
    screen.blit(score_surface, (10, 80))
    moedas.draw(screen)
    screen.blit(barco.image, barco.rect)

    # Mostrar quantidade de moedas capturadas
    info_text = f'Moedas: {barco.carga}/{barco.max_carga}'
    nivel_text = f'Nível: {nivel}'
    screen.blit(FONT.render(info_text, True, (255, 255, 255)), (10, 10))
    screen.blit(FONT.render(nivel_text, True, (255, 255, 255)), (10, 50))

    # Se desejar, pode aqui aumentar o nível
    if barco.carga >= barco.max_carga:
        #aparecer o posto
        nivel += 1
        if nivel > 4:
            nivel = 4  # máximo nível
        qtd_moedas, v_min, v_max = configurar_dificuldade(nivel)

    # Atualiza a tela
    pygame.display.flip()

# Encerra o pygame ao sair do loop
pygame.quit()
sys.exit()
