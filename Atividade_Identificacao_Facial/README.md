# Atividade separada - Identificacao Facial

Script Python para identificacao facial local usando OpenCV. A atividade tem tres etapas: cadastrar amostras autorizadas, treinar um modelo LBPH e identificar rostos pela webcam, stream ou imagem.

> Use somente com pessoas que autorizaram o cadastro. As amostras e o modelo ficam locais nesta pasta e devem ser tratados como dados sensiveis.

## Instalar dependencias

```bash
cd Atividade_Identificacao_Facial
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Se o seu sistema usa `python` em vez de `python3`, pode trocar nos comandos. No Windows, a ativacao do ambiente virtual costuma ser:

```powershell
.venv\Scripts\activate
```

## Como usar

### 1. Cadastrar uma pessoa

```bash
python3 identificacao_facial.py cadastrar --nome "Pessoa 1" --amostras 40
```

Dicas:
- Olhe para a camera e varie levemente o angulo do rosto.
- Pressione `q` para encerrar antes do limite.
- As imagens ficam em `amostras/<nome>/`.

Tambem e possivel usar uma URL de stream, por exemplo de uma ESP32-CAM:

```bash
python3 identificacao_facial.py cadastrar --nome "Pessoa 1" --camera http://IP_DA_CAMERA/stream
```

### 2. Treinar o modelo

```bash
python3 identificacao_facial.py treinar
```

O treino gera:
- `modelo/faces_lbph.yml`
- `modelo/labels.json`

### 3. Identificar pela webcam

```bash
python3 identificacao_facial.py identificar --camera 0
```

### 4. Identificar em uma imagem

```bash
python3 identificacao_facial.py identificar --imagem foto.jpg --salvar resultado.jpg --sem-janela
```

## Parametros uteis

- `--amostras 60`: aumenta a quantidade de capturas no cadastro.
- `--intervalo 0.15`: reduz o intervalo entre amostras salvas.
- `--limite 65`: deixa a identificacao mais exigente. No LBPH, distancia menor indica maior semelhanca.
- `--min-rosto 100`: ignora rostos pequenos na imagem.

## Estrutura

```text
Atividade_Identificacao_Facial/
|-- README.md
|-- identificacao_facial.py
|-- requirements.txt
|-- amostras/
|   `-- .gitkeep
`-- modelo/
    `-- .gitkeep
```

`amostras/` e `modelo/` estao no `.gitignore` para evitar versionar imagens de pessoas e modelos gerados.
