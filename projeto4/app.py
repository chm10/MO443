import click
import wget
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import cv2

#--- Configuracao de comandos em terminal

# Variavel de ambiente padrao
host = Path(".").cwd()
_output = (Path(host) / "result").absolute()
_output.mkdir(exist_ok=True, parents=True)

# Faz o visual ficar mais amigavel
@click.group()
def clicode():
    pass

# Comando para criar ambiente de exemplo e baixar imagem
@clicode.command()
@click.option('path', '--path',type=click.Path(),default=str(_output))
def download(path):
    """Cria uma ambiente de exemplo e baixa imagens."""
    setup(Path(path))

# Comando para colocar uma mensagem dentro da imagem
@clicode.command()
@click.option('file', '--image','-i',type=click.Path(),default=str(_output / 'baboon.png'))
@click.option('msg', '--message_file','-mf',type=click.Path() ,default=str(_output / 'sample.txt'))
@click.option('channel','--channel','-c', type=click.IntRange(0, 2, clamp=True),default=0)
def codefile(file,msg,channel):
    """Comando para colocar uma mensagem dentro da imagem"""
    img = loadImg(file)
    f = open(msg, "r")
    message = f.read()
    f.close()
    custom_img = cv2.cvtColor(code(img[list(img.keys())[0]],phrasetobyte(message),channel),cv2.COLOR_RGB2BGR)
    filename = Path(file).parent / f"{Path(file).stem}_coded.png" 
    print(filename)
    if not cv2.imwrite(str(filename),custom_img):
        raise Exception("Could not write image")

# Faz o visual ficar mais agradavel
@click.group()
def clidecode():
    pass

@clicode.command()
@click.option('file', '--image','-i',type=click.Path(),default=str(_output / 'baboon.png'))
def display_bits(file):
    """
    Essa função exibe uma imagem com apenas bit 0, 1, 2 e 7
    """
    bits = [0,1,2,7]
    img = loadImg(file)
    label = list(img.keys())[0]
    img = img[label]
    _shape = img.shape
    imgs2 = []
    for i in bits:
        imgs2.append(applyMask(img.flatten(),i).reshape(_shape))
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2) # Inicializa um espaço para 4 imagens
    fig.suptitle(f"Imagens")
    fig.set_size_inches(15,15)
    for ax, img,b in zip(fig.get_axes(),imgs2,bits): # exibe imagens
        ax.imshow(img)
        ax.label_outer()
        ax.set_xticks([]), ax.set_yticks([])
        ax.set_title(f"{label} bit={b}")
    plt.show()

# Comando que extrai a mensagem de dentro da imagem
@clidecode.command()
@click.option('file', '--image','-i',type=click.Path(),default=str(_output / 'baboon_coded.png'))
@click.option('channel','--channel','-c', type=click.IntRange(0, 2, clamp=True),default=0)
def decodefile(file, channel):
    """Comando que extrai a mensagem de dentro da imagem."""
    img = loadImg(file)
    msg = decode(img[list(img.keys())[0]],channel)
    print(msg)
    
# Monta os comandos
cli = click.CommandCollection(sources=[clicode, clidecode])

#---- Algoritmo

def setup(path):
    """
    Essa função é responsável por baixar as imagens de exemplo e criar um arquivo de txt.
    """
    [i.unlink() for i in path.rglob("*.txt")] # Procura por txt  e deleta
    [i.unlink() for i in path.rglob("*.png")] # Procura por imagens png e deleta
    wget.download("https://www.ic.unicamp.br/~helio/imagens_coloridas/baboon.png",out=str(path))
    wget.download("https://www.ic.unicamp.br/~helio/imagens_coloridas/monalisa.png",out=str(path))
    wget.download("https://www.ic.unicamp.br/~helio/imagens_coloridas/peppers.png", out=str(path))
    wget.download("https://www.ic.unicamp.br/~helio/imagens_coloridas/watch.png", out=str(path))
    f = open(path / "sample.txt", "a")
    f.write("This is a sample to make test!") # escreve a mensagem secreta
    f.close()
    
def loadImg(path):
    """
    Essa função é responsável por carregar uma imagem. Path do pathlib é utilizada para pegar uma imagem
    com final png da variável path o conteúdo vetorizado é armazenado no dicionario de img. 
    E o nome dessa imagem fica salvo no dict como referencia na hora salvar.
    """
    img = {}
    img[Path(path).stem] = cv2.cvtColor(cv2.imread(f"{path}"), cv2.COLOR_BGR2RGB) # Carrega imagens BGR para RGB
    return img

def phrasetobyte(_phrase):
    """
    Essa função é responsável por pegar uma variavel string  e converter cada palavra
    em representação de byte e colocar numa lista.
    """
    _phrase = bytearray(_phrase,"utf8")
    _string = []
    for i in list(bytes(_phrase)):
        _byte = []
        while (i>0):
            _byte.append(i%2)
            i = i//2
        while(len(_byte) < 8):
            _byte.append(0)
        _byte.reverse()
        _string.append(_byte)
    return _string

def code(img,phrase,channel):
    """
    Essa função é responsável por pegar uma imagem RGB e a frase em byte e passar para um canal da imagem.
    """
    _shape = img.shape
    img = img.flatten()
    _phrase = np.array(phrase).flatten()
    for idx, v in enumerate(img):
        if channel < 3:
            img[idx] &= ~np.uint8(1<<(channel))
            if  idx < len(_phrase) :
                if  (_phrase[idx]):
                    img[idx] = v|np.uint8(_phrase[idx]<<channel)
    return img.reshape(_shape).astype(np.uint8)

def applyMask(img,bit):
  assert (bit>= 0) and (bit <=7), "Bit need to be between (0) and (7)"
  new_img = img&int(format(1 << bit,'08b'),2)
  return new_img*255

def decode(img,_channel):
    """
    Essa função é responsável por pegar uma imagem RGB e extrair a mensagem.
    """
    _string2 = []
    _size = img.size
    for idx, v in enumerate(img.flatten()):
        v &= np.uint8(1<<(_channel))
        if v > 0:
            _string2.append(1)
        else:
            _string2.append(0)
    rec = []
    for i in np.array(_string2).reshape(_size//8,8):
        rec.append(int(''.join(map(str, i)), 2)) 
    msg = ''.join([chr(i) for i in rec]).replace(chr(0),"")
    return msg

if __name__ == '__main__':
    cli()