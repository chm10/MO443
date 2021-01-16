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
def app():
    pass

# Comando para colocar uma mensagem dentro da imagem
@app.command()
@click.option('angle','--angle','-a', type=click.IntRange(-360, 360, clamp=True))
@click.option('scale','--scale','-e', type=float)
@click.option('dimension','--dimension','-d', nargs=2, type=int)
@click.option('method', '--method','-m',required=True)
@click.option('input', '--input','-i',type=click.Path(),default=str(_output / 'baboon.png'))
@click.option('output', '--output','-o',type=click.Path())
def prog(angle,scale,dimension,method,input,output):
    """Comando fazer interpolacao o metodo pode ser [vizinho, bilinear, bicubic, lagrange]"""
    print(f"{angle},{scale},{dimension},{method},{input},{output}")
    if(((angle!=None) + (scale!=None) + (len(dimension)>0)) == 1):
        img = loadImg(input)
        label = list(img.keys())[0]
        img = img[label]
        if method == "vizinho":
            custom_img = cv2.cvtColor(vizinhoproximo(img,scale,angle,dimension).astype(np.uint8),cv2.COLOR_RGB2BGR)
        elif method == "bilinear":
            custom_img = cv2.cvtColor(bilinear(img,scale,angle,dimension).astype(np.uint8),cv2.COLOR_RGB2BGR)
        elif method == "bicubic":
            custom_img = cv2.cvtColor(bicubic(img,scale,angle,dimension).astype(np.uint8),cv2.COLOR_RGB2BGR)
        elif method == "lagrange":
            custom_img = cv2.cvtColor(lagrange(img,scale,angle,dimension).astype(np.uint8),cv2.COLOR_RGB2BGR)
        else:
            raise Exception("Metodo nao disponivel")
        if scale != None:
          choose = f"{method}_{scale}"
        elif angle != None:
          choose = f"{method}_{angle}"
        elif len(dimension) > 0:
          choose = f"{method}_{dimension}"
        if output==None:
            filename = Path(input).parent / f"{Path(input).stem}_{choose}.png"  
        else:
            filename = output
        print(filename)
        if not cv2.imwrite(str(filename),custom_img):
            raise Exception("Could not write image")
    elif (((angle!=None) + (scale!=None) + (len(dimension))) == 0):
        raise Exception("Faltando um argumento de transformacao")
    else:
        raise Exception("Esse algoritmo nao suporta mais que uma transformacao")

# Faz o visual ficar mais agradavel
@click.group()
def env():
    pass

# Comando para criar ambiente de exemplo e baixar imagem
@env.command()
@click.option('path', '--path',type=click.Path(),default=str(_output))
def download(path):
    """Cria uma ambiente de exemplo e baixa imagens."""
    setup(Path(path))
    
# Monta os comandos
cli = click.CommandCollection(sources=[env, app])

#---- Algoritmo

def setup(path):
    """
    Essa função é responsável por baixar as imagens de exemplo e criar um arquivo de txt.
    """
    [i.unlink() for i in path.rglob("*.png")] # Procura por imagens png e deleta
    wget.download("https://www.ic.unicamp.br/~helio/imagens_png/baboon.png",out=str(path))
    wget.download("https://www.ic.unicamp.br/~helio/imagens_png/butterfly.png",out=str(path))
    wget.download("https://www.ic.unicamp.br/~helio/imagens_png/city.png", out=str(path))
    wget.download("https://www.ic.unicamp.br/~helio/imagens_png/house.png", out=str(path))
    wget.download("https://www.ic.unicamp.br/~helio/imagens_png/seagull.png", out=str(path))

def cropImg(img,h,w,p):
    new_h, new_w = np.min([int(h*p),int(img.shape[0])]), np.min([int(w*p),int(img.shape[1])])
    return img[w:new_h,h:new_w,:]


# Comando para criar ambiente de exemplo e baixar imagem
@env.command()
@click.option('input', '--input','-i',type=click.Path(),default=str(_output / 'baboon.png'))
@click.option('dimension','--dimension','-d', nargs=2, type=int,required=True)
@click.option('dimensionscale','--ds','-ds', type=float, default=1.1)
@click.option('scale','--scale','-e', type=float,default=2)
def crop(input,dimension,dimensionscale,scale):
    """
    Funcao para mostrar imagem com interpolacao
    """
    img = loadImg(input)
    label = list(img.keys())[0]
    img = img[label]
    cropped = cropImg(img,dimension[0],dimension[1],dimensionscale)
    methods = ["vizinho","bilinear","bicubic","lagrange"] 
    imgs2 = []
    angle = None
    dimension = ()
    imgs2.append(cv2.cvtColor(vizinhoproximo(cropped,scale,angle,dimension).astype(np.uint8),cv2.COLOR_RGB2BGR))
    imgs2.append(cv2.cvtColor(bilinear(cropped,scale,angle,dimension).astype(np.uint8),cv2.COLOR_RGB2BGR))
    imgs2.append(cv2.cvtColor(bicubic(cropped,scale,angle,dimension).astype(np.uint8),cv2.COLOR_RGB2BGR))
    imgs2.append(cv2.cvtColor(lagrange(cropped,scale,angle,dimension).astype(np.uint8),cv2.COLOR_RGB2BGR))

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2) # Inicializa um espaço para 4 imagens
    fig.suptitle(f"Imagens")
    fig.set_size_inches(15,15)
    for ax, img,b in zip(fig.get_axes(),imgs2,methods): # exibe imagens
        ax.imshow(img)
        ax.label_outer()
        ax.set_xticks([]), ax.set_yticks([])
        ax.set_title(f"{label} method={b}")
    plt.show()
# Monta os comandos
cli = click.CommandCollection(sources=[env, app])

def loadImg(path):
    """
    Essa função é responsável por carregar uma imagem. Path do pathlib é utilizada para pegar uma imagem
    com final png da variável path o conteúdo vetorizado é armazenado no dicionario de img. 
    E o nome dessa imagem fica salvo no dict como referencia na hora salvar.
    """
    img = {}
    img[Path(path).stem] = cv2.cvtColor(cv2.imread(f"{path}"), cv2.COLOR_BGR2RGB) # Carrega imagens BGR para RGB
    return img

def extractScale(img,new_height, new_width):
    """
    Essa função foi criado para calcular qual é o fator de escala do eixo x e y ele pega o tamanho da dimensao
    e divide pela dimensao original
    """
    height, width, channel = img.shape
    return (new_height/height, new_width/width)

def extractDimension(img,scale):
    height, width, channel = img.shape
    return (round(height*scale), round(width*scale),3)

def transformScale(p,s):
    S = np.diag([s[0],s[1]])
    P = np.array(p).T
    return np.dot(P,S)[0:2]

def iTransformScale(p,s):

    S = np.diag([s[0],s[1],1])
    P = np.array([p[0],p[1],1]).T
    return np.linalg.solve(S, P)[0:2]

def transformGrade(p,g):
    G =  np.array([np.cos(g), -np.sin(g),0 , np.sin(g), np.cos(g),0,0,0,1]).reshape((3,3))
    P = np.array([p[0],p[1],1]).T
    return np.dot(G,P)[0:2]

def iTransformGrade(p,g):
    G =  np.array([np.cos(g), -np.sin(g),0 , np.sin(g), np.cos(g),0,0,0,1]).reshape((3,3))
    P = np.array([p[0],p[1],1]).T
    return np.linalg.solve(G, P)[0:2]

def vizinhoproximo(img,scale,angle,dimension):
    if(scale!=None):
        new_img = np.zeros(extractDimension(img,scale))
        ref_h, ref_w, ref_c = new_img.shape
        ref_e = (scale, scale)
        for i in range(ref_h):
            for j in range(ref_w):
                copy_x, copy_y = tuple(iTransformScale((i,j), ref_e).round().astype(int))
                if copy_x < img.shape[0] and copy_y < img.shape[1]:
                    new_img[i,j,0] = img[copy_x, copy_y,0]
                    new_img[i,j,1] = img[copy_x, copy_y,1]
                    new_img[i,j,2] = img[copy_x, copy_y,2]
    elif(len(dimension)>0):
        new_img = np.zeros((dimension[0], dimension[1], 3))
        ref_h, ref_w, ref_c = new_img.shape
        ref_e = extractScale(img,dimension[0],dimension[1])
        for i in range(ref_h):
            for j in range(ref_w):
                copy_x, copy_y = tuple(iTransformScale((i,j), ref_e).round().astype(int))
                if copy_x < img.shape[0] and copy_y < img.shape[1]:
                    new_img[i,j,0] = img[copy_x, copy_y,0]
                    new_img[i,j,1] = img[copy_x, copy_y,1]
                    new_img[i,j,2] = img[copy_x, copy_y,2]
    elif(angle!=None):
        #max_len = int(np.sqrt(img.shape[0]**2 + img.shape[1]**2))
        new_img = np.zeros(img.shape)
        ref_h, ref_w, ref_c = new_img.shape
        ref_a = np.deg2rad(angle)
        mid_row = (ref_h+1)//2
        mid_col = (ref_w+1)//2
        for i in range(ref_h):
            for j in range(ref_w):
                xoff = i - mid_row
                yoff = j - mid_col

                copy_x, copy_y = np.round(iTransformGrade((xoff,yoff),ref_a)).astype(int)
                copy_x += mid_row
                copy_y += mid_col
                if copy_x >= 0 and copy_y >= 0  and copy_x < img.shape[0] and copy_y < img.shape[1]:
                    new_img[i,j,:] = img[copy_x,copy_y,:]
    return new_img

def bilinear(img,scale,angle,dimension):
    if(scale!=None):
        new_img = np.zeros(extractDimension(img,scale))
        ref_h, ref_w, ref_c = new_img.shape
        ref_e = (scale, scale)
        for i in range(ref_h):
            for j in range(ref_w):
                copy_x, copy_y = tuple(iTransformScale((i,j), ref_e))
                copy_x_prev = copy_x.astype(int)
                copy_y_prev = copy_y.astype(int)
                copy_x_next = copy_x_prev + 1
                copy_y_next = copy_y_prev + 1
                dy_next = copy_y_next - copy_y
                dx_next = copy_x_next - copy_x
                dy = 1 - dy_next
                dx = 1  - dx_next
                if copy_x_prev >= 0 and copy_y_prev >= 0 and copy_x_next < img.shape[0] and copy_y_next < img.shape[1]:
                    for c in range(3):
                        new_img[i][j][c] = dy * (img[copy_x_prev][copy_y_next][c] * dx_next + img[copy_x_next][copy_y_next][c] * dx) \
                        + dy_next * (img[copy_x_prev][copy_y_prev][c] * dx_next + img[copy_x_next][copy_y_prev][c] * dx)
    elif(len(dimension)>0):
        new_img = np.zeros((dimension[0], dimension[1], 3))
        ref_h, ref_w, ref_c = new_img.shape
        ref_e = extractScale(img,dimension[0],dimension[1])
        for i in range(ref_h):
            for j in range(ref_w):
                copy_x, copy_y = tuple(iTransformScale((i,j), ref_e))
                copy_x_prev = copy_x.astype(int)
                copy_y_prev = copy_y.astype(int)
                copy_x_next = copy_x_prev + 1
                copy_y_next = copy_y_prev + 1
                dy_next = copy_y_next - copy_y
                dx_next = copy_x_next - copy_x
                dy = 1 - dy_next
                dx = 1  - dx_next
                if copy_x_prev >= 0 and copy_y_prev >= 0 and copy_x_next < img.shape[0] and copy_y_next < img.shape[1]:
                    for c in range(3):
                        new_img[i][j][c] = dy * (img[copy_x_prev][copy_y_next][c] * dx_next + img[copy_x_next][copy_y_next][c] * dx) \
                        + dy_next * (img[copy_x_prev][copy_y_prev][c] * dx_next + img[copy_x_next][copy_y_prev][c] * dx)
    elif(angle!=None):
        new_img = np.zeros(img.shape)
        ref_h, ref_w, ref_c = new_img.shape
        ref_a = np.deg2rad(angle)
        mid_row = (ref_h+1)//2
        mid_col = (ref_w+1)//2
        for i in range(ref_h):
            for j in range(ref_w):
                xoff = i - mid_row
                yoff = j - mid_col

                copy_x, copy_y = iTransformGrade((xoff,yoff),ref_a)
                copy_x += mid_row
                copy_y += mid_col
                copy_x_prev = copy_x.astype(int)
                copy_y_prev = copy_y.astype(int)
                copy_x_next = copy_x_prev + 1
                copy_y_next = copy_y_prev + 1
                dy_next = copy_y_next - copy_y
                dx_next = copy_x_next - copy_x
                dy = 1 - dy_next
                dx = 1  - dx_next
                if copy_x_prev >= 0 and copy_y_prev >= 0 and copy_x_next < img.shape[0] and copy_y_next < img.shape[1]:
                    for c in range(3):
                        new_img[i][j][c] = dy * (img[copy_x_prev][copy_y_next][c] * dx_next + img[copy_x_next][copy_y_next][c] * dx) \
                        + dy_next * (img[copy_x_prev][copy_y_prev][c] * dx_next + img[copy_x_next][copy_y_prev][c] * dx)
    return new_img

def P(t):
    return t if t > 0.0  else 0 

def R(s):
    s = float(s)
    return (1/6) * ( (P(s+2)**3) -4*(P(s+1)**3) +6* (P(s)**3) -4*(P(s-1)**3) )

def bicubic(img,scale,angle,dimension):
    if(scale!=None):
        new_img = np.zeros(extractDimension(img,scale))
        ref_h, ref_w, ref_c = new_img.shape
        for i in range(ref_h):
            for j in range(ref_w):
                copy_x = i * (img.shape[0]/new_img.shape[0]) 
                copy_y = j * (img.shape[1]/new_img.shape[1])
                
                copy_x_prev = int(np.floor(copy_x))
                copy_y_prev = int(np.floor(copy_y))
                dx = copy_x - copy_x_prev
                dy = copy_y - copy_y_prev
                for n in range(-1,3):
                    for m in range(-1,3):
                        copy_x_next = copy_x_prev + m
                        copy_y_next = copy_y_prev + n
                        if copy_x_next >= 0 and copy_x_next >= 0 and copy_x_next < img.shape[0] and copy_y_next < img.shape[1]:
                            new_img[i,j,:] += img[copy_x_next,copy_y_next,:] * R(m-dx) * R(dy - n)
    elif(len(dimension)>0):
        new_img = np.zeros((dimension[0], dimension[1], 3))
        ref_h, ref_w, ref_c = new_img.shape
        for i in range(ref_h):
            for j in range(ref_w):
                copy_x = i * (img.shape[0]/new_img.shape[0]) 
                copy_y = j * (img.shape[1]/new_img.shape[1])
                
                copy_x_prev = int(np.floor(copy_x))
                copy_y_prev = int(np.floor(copy_y))
                dx = copy_x - copy_x_prev
                dy = copy_y - copy_y_prev
                for n in range(-1,3):
                    for m in range(-1,3):
                        copy_x_next = copy_x_prev + m
                        copy_y_next = copy_y_prev + n
                        if copy_x_next >= 0 and copy_x_next >= 0 and copy_x_next < img.shape[0] and copy_y_next < img.shape[1]:
                            new_img[i,j,:] += img[copy_x_next,copy_y_next,:] * R(m-dx) * R(dy - n)
    elif(angle!=None):
        new_img = np.zeros(img.shape)
        ref_h, ref_w, ref_c = new_img.shape
        ref_a = np.deg2rad(angle)
        mid_row = (ref_h+1)//2
        mid_col = (ref_w+1)//2
        for i in range(ref_h):
            for j in range(ref_w):
                xoff = i  - mid_row
                yoff = j  -  mid_col

                copy_x, copy_y = iTransformGrade((xoff,yoff),ref_a)
                copy_x += mid_row
                copy_y += mid_col
                copy_x_prev = int(np.floor(copy_x))
                copy_y_prev = int(np.floor(copy_y))
                dx = copy_x - copy_x_prev
                dy = copy_y - copy_y_prev
                for n in range(-1,3):
                    for m in range(-1,3):
                        copy_x_next = copy_x_prev + m
                        copy_y_next = copy_y_prev + n
                        if copy_x_next >= 0 and copy_y_next >= 0 and copy_x_next < img.shape[0] and copy_y_next < img.shape[1]:
                            new_img[i,j,:] += img[copy_x_next,copy_y_next,:] * R(m-dx) * R(dy - n)
    return new_img
def if_valid(x,y,x_max,y_max):
    return True if (x >= 0) & (y >= 0) & (x < x_max) & (y < y_max) else False

def L(img,n,x,y,dx):
    a1 = 0
    a2 = 0 
    a3 = 0
    a4 = 0 
    if if_valid(x-1,y+n-2,img.shape[0],img.shape[1]):
        a1 = (-dx*(dx-1)*(dx-2)*img[x-1,y+n-2,:])/6
    if if_valid(x,y+n-2,img.shape[0],img.shape[1]):
        a2 = ((dx+1)*(dx-1)*(dx-2)*img[x,y+n-2,:])/2
    if if_valid(x+1,y+n-2,img.shape[0],img.shape[1]):
        a3 = ((-dx)*(dx+1)*(dx-2)*img[x+1,y+n-2,:])/2
    if if_valid(x+2,y+n-2,img.shape[0],img.shape[1]):
        a4 = ((dx)*(dx+1)*(dx-1)*img[x+2,y+n-2,:])/6
    return a1+a2+a3+a4

def f_(img,x,y,dx,dy):
    a1 = (-dy * (dy-1) * (dy-2) * L(img,1,x,y,dx))/6
    a2 = ((dy+1)*(dy-1)*(dy-2)*L(img,2,x,y,dx))/2
    a3 = (-dy*(dy+1)*(dy-2)*L(img,3,x,y,dx))/2
    a4 = (dy*(dy+1)*(dy-1)*L(img,4,x,y,dx))/6
    return a1+a2+a3+a4
def lagrange(img,scale,angle,dimension):
    if(scale!=None):
        new_img = np.zeros(extractDimension(img,scale))
        ref_h, ref_w, ref_c = new_img.shape
        for i in range(ref_h):
            for j in range(ref_w):
                copy_x = i * (img.shape[0]/new_img.shape[0]) 
                copy_y = j * (img.shape[1]/new_img.shape[1])
                
                copy_x_prev = int(np.floor(copy_x))
                copy_y_prev = int(np.floor(copy_y))
                dx = copy_x - copy_x_prev
                dy = copy_y - copy_y_prev
                new_img[i,j,:] = f_ (img,copy_x_prev,copy_y_prev,dx,dy)
    elif(len(dimension)>0):
        new_img = np.zeros((dimension[0], dimension[1], 3))
        ref_h, ref_w, ref_c = new_img.shape
        for i in range(ref_h):
            for j in range(ref_w):
                copy_x = i * (img.shape[0]/new_img.shape[0]) 
                copy_y = j * (img.shape[1]/new_img.shape[1])
                
                copy_x_prev = int(np.floor(copy_x))
                copy_y_prev = int(np.floor(copy_y))
                dx = copy_x - copy_x_prev
                dy = copy_y - copy_y_prev
                new_img[i,j,:] = f_ (img,copy_x_prev,copy_y_prev,dx,dy)
    elif(angle!=None):
        new_img = np.zeros(img.shape)
        ref_h, ref_w, ref_c = new_img.shape
        ref_a = np.deg2rad(angle)
        mid_row = (ref_h+1)//2
        mid_col = (ref_w+1)//2
        for i in range(ref_h):
            for j in range(ref_w):
                xoff = i  - mid_row
                yoff = j  -  mid_col

                copy_x, copy_y = iTransformGrade((xoff,yoff),ref_a)
                copy_x += mid_row
                copy_y += mid_col
                copy_x_prev = int(np.floor(copy_x))
                copy_y_prev = int(np.floor(copy_y))
                dx = copy_x - copy_x_prev
                dy = copy_y - copy_y_prev
                new_img[i,j,:] = f_ (img,copy_x_prev,copy_y_prev,dx,dy)
    return new_img



if __name__ == '__main__':
    cli()
