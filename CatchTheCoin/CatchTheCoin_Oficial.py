#
# CATCH THE COINS: A CACHORRINHA QUE CAÇA MOEDAS
#
# Nome: Milena Cardoso Lopes
# Professor: Filipo Novo
# Disciplina: Algoritmos e Programação
# Curso: Ciência da Computação
#
import pygame
import random
import sys

pygame.init()

# Carregar os sons
som_aviso = pygame.mixer.Sound(r'Assets/Audio/latido.mp3') #trocar por latido
som_beep = pygame.mixer.Sound(r'Assets/Audio/beep.mp3')

# Carregar a música de fundo
pygame.mixer.music.load(r'Assets/Audio/musicafundo.mp3')  # Caminho da música
pygame.mixer.music.set_volume(0.5)  # Opcional: ajuste o volume entre 0.0 e 1.0
pygame.mixer.music.play(-1, 0.0)  # Toca a música em loop (o '-1' significa loop infinito)

# Configurações iniciais
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Navio Cata Moedas!!!")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont(None, 36)
MOEDA_TAMANHO = (25, 25)

# Carregar a imagem do fundo de acordo com o nível
backgrounds = {
    1: pygame.transform.smoothscale(pygame.image.load(r'Assets/PNG/parque2.png').convert_alpha(), (WIDTH, HEIGHT)),
    2: pygame.transform.smoothscale(pygame.image.load(r'Assets/PNG/parque1.png').convert_alpha(), (WIDTH, HEIGHT)),
    3: pygame.transform.smoothscale(pygame.image.load(r'Assets/PNG/parque4.png').convert_alpha(), (WIDTH, HEIGHT)),
    4: pygame.transform.smoothscale(pygame.image.load(r'Assets/PNG/parque3.png').convert_alpha(), (WIDTH, HEIGHT))
}

# Casinha (porto)
casinha_img = pygame.image.load(r'Assets/PNG/casinha1.png').convert_alpha()
casinha_img = pygame.transform.smoothscale(casinha_img, (300, 300))  # Tamanho ajustável
casinha_rect = casinha_img.get_rect(bottomright=(WIDTH - 10, HEIGHT - 100))

# Carregar a imagem base da cachorrinha
img_direita = pygame.image.load(r'Assets/PNG/cachorrinha1.png').convert_alpha()

# Proporção da imagem da cachorrinha
escala = 0.35
largura = int(img_direita.get_width() * escala)
altura = int(img_direita.get_height() * escala)
img_direita = pygame.transform.smoothscale(img_direita, (largura, altura))

# Gera automaticamente a versão espelhada para o lado esquerdo
img_esquerda = pygame.transform.flip(img_direita, True, False)

# Função para configurar a dificuldade
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
        self.image = img_direita  # começa virada pra direita
        self.direcao = 'direita'
        self.rect = self.image.get_rect(midbottom=(WIDTH//2, HEIGHT - 120))
        self.speed = 8
        self.carga = 0
        self.max_carga = 100

    def update(self, keys_pressed):
        if keys_pressed[pygame.K_LEFT]:
            self.rect.x -= self.speed
            if self.direcao != 'esquerda':
                self.image = img_esquerda
                self.direcao = 'esquerda'
        elif keys_pressed[pygame.K_RIGHT]:
            self.rect.x += self.speed
            if self.direcao != 'direita':
                self.image = img_direita
                self.direcao = 'direita'

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

    def voltar_ao_porto(self):
        self.rect.midbottom = (WIDTH // 2, HEIGHT - 120)
        self.carga = 0

# Variáveis de controle
nivel = 1
qtd_moedas, v_min, v_max = configurar_dificuldade(nivel)
moedas = pygame.sprite.Group()
em_descarga = False
pontos = 0
mostrar_casinha = False
jogo_finalizado = False


# Criar moedas iniciais
for _ in range(qtd_moedas):
    tipo = random.choice(['ouro', 'prata', 'bronze'])
    x = random.randint(0, WIDTH - 20)
    y = random.randint(-100, -10)
    moedas.add(Moeda(x, y, tipo))

# Instanciar o barco
barco = Barco()

# Loop principal do jogo
running = True
while running:
    clock.tick(60)  # 60 frames por segundo

    # Processar eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            # Reinicia todas as variáveis do jogo
            if jogo_finalizado and event.key == pygame.K_r:
                nivel = 1
                qtd_moedas, v_min, v_max = configurar_dificuldade(nivel)
                moedas.empty()
                for _ in range(qtd_moedas):
                    tipo = random.choice(['ouro', 'prata', 'bronze'])
                    x = random.randint(0, WIDTH - 20)
                    y = random.randint(-100, -10)
                    moedas.add(Moeda(x, y, tipo))
                barco.voltar_ao_porto()
                barco.carga = 0
                pontos = 0
                em_descarga = False
                mostrar_casinha = False
                jogo_finalizado = False

    keys = pygame.key.get_pressed()

# Se o barco estiver carregando até o limite, inicia o descarregamento
    if not em_descarga and barco.carga >= barco.max_carga and not jogo_finalizado:
        som_aviso.play()
        mostrar_casinha = True
        em_descarga = True

    # Atualiza movimento do barco
    barco.update(keys)

# Atualiza as moedas apenas se o barco não estiver descarregando
    if not em_descarga:
        moedas.update()

    # Permite que o barco continue coletando moedas mesmo em modo de descarregamento
    colisoes = pygame.sprite.spritecollide(barco, moedas, True)
    for moeda in colisoes:
        barco.carga += VALOR_MOEDAS[moeda.tipo]
        som_beep.play()
        pontos += 1

    # Garantir que o número de moedas esteja constante apenas quando não estiver em descarregamento
    if not em_descarga and len(moedas) < qtd_moedas:
        tipo = random.choice(['ouro', 'prata', 'bronze'])
        x = random.randint(0, WIDTH - 20)
        y = random.randint(-100, -10)
        moedas.add(Moeda(x, y, tipo))

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

# Desenhar a tela
    screen.blit(backgrounds[nivel], (0, 0))  # Muda o fundo conforme o nível
    if mostrar_casinha:
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

# Mostrar instruções de descarregamento
    if em_descarga and mostrar_casinha and not jogo_finalizado:
        if barco.rect.colliderect(casinha_rect):
            msg = FONT.render("Pressione 'E' para descarregar", True, (255, 255, 0))
        else:
            msg = FONT.render("Vá até a casinha para descarregar", True, (255, 255, 255))
        screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT - 70))

    # Bloco de Descarregamento e Passagem de Fase
    if em_descarga and mostrar_casinha and barco.rect.colliderect(casinha_rect):
        if keys[pygame.K_e]:
            if nivel < 4:
                barco.voltar_ao_porto()
                barco.carga = 0
                em_descarga = False
                mostrar_casinha = False

                nivel += 1
                qtd_moedas, v_min, v_max = configurar_dificuldade(nivel)
            else:
                jogo_finalizado = True
                em_descarga = False
                mostrar_casinha = False

    # Mostrar mensagem de reinício quando o jogo finalizar
    if jogo_finalizado:
        texto_parabens = FONT.render("Parabéns! Você concluiu todos os níveis!", True, (0, 0, 0))
        texto_reiniciar = FONT.render("Pressione 'R' para reiniciar o jogo.", True, (0, 0, 0))

        # Centralizar horizontalmente e empilhar verticalmente
        x_central = WIDTH // 2
        y_central = HEIGHT // 2

        screen.blit(texto_parabens, (x_central - texto_parabens.get_width() // 2, y_central - 30))
        screen.blit(texto_reiniciar, (x_central - texto_reiniciar.get_width() // 2, y_central + 10))

    # Atualiza a tela
    pygame.display.flip()

# Encerra o pygame ao sair do loop
pygame.quit()
sys.exit()
