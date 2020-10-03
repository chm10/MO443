## Baixe o Git

* Baixe e instale o Git por este link [link](https://git-scm.com/).

## Baixe o repositório
`````
git https://github.com/chm10/MO443.git
`````


Você pode executar os trabalhos usando Anaconda ou Docker

---

# Como executar
## Instale o Anaconda (Modo rápido)

* Baixe e instale o Anaconda usando este  [link](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html#installing-conda-on-a-system-that-has-other-python-installations-or-packages)

* Abra a linha de comando do anaconda e vá até pasta do projeto

* Para executar o jupyter notebook (Local)

###  Para executar o jupyter

#### Crie um ambiente
`````powershell
conda create -y --name mo443_env_231867 python==3.6.9 
`````

#### Ative o ambiente 
`````powershell
conda activate mo443_env_231867
`````

#### Instale os requisitos para executar o projeto
`````powershell
pip install -r requirements.txt
`````

#### Instale o repositório 
`````powershell
pip install -e extra_lib/
`````

#### Exemplo para rodar um programa
`````powershell
python main.py
`````

#### Exempo para abrir um notebook

`````powershell
jupyter notebook
`````

Lembre-se: Vá até a pasta do projeto antes de rodar os comandos no Terminal do Anaconda


#### Desintale o ambiente
`````powershell
conda activate base
conda remove --name mo443_env_231867 --all
`````

---
# Usando Docker
## Instale o Docker

   Baixe e instale o Docker usando este [link](https://www.docker.com/products/docker-desktop)

#### Baixe uma imagem simples com terminal/python

`````powershell
docker build -t "python_light" .
`````

#### Inicialize um container com bash com as configurações do ambiente
Existe dois modo o Developement mode (Se você quizer modificar o conteúdo da pasta do repositório)
`````powershell
docker run --rm -it -p 8888:8888 -v "$(pwd):/app" python_light
`````

Deploy mode (Se você modificar dentro do container essa alteração não refletira na pasta do projeto)
`````powershell
docker run --rm -it -p 8888:8888  python_light
`````

#### Dentro do container para rodar o jupyter lab
**Você precisa copiar o link e colar no navegador para conseguir acessar o jupyter-lab. Ele não abrirá sozinho.**
`````bash
root@hash:/app# ./jupyter-lab.sh
`````

#### Desinstalar a imagem 
`````powershell
docker rmi python_light
`````
