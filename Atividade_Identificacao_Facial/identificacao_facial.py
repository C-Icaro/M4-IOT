"""Atividade separada: identificacao facial local com OpenCV.

Fluxo principal:
    1. Cadastrar amostras de uma pessoa autorizada.
    2. Treinar um modelo LBPH com as amostras cadastradas.
    3. Identificar rostos em uma webcam, stream ou imagem.

Exemplos:
    python identificacao_facial.py cadastrar --nome "Pessoa 1"
    python identificacao_facial.py treinar
    python identificacao_facial.py identificar --camera 0
    python identificacao_facial.py identificar --imagem foto.jpg --salvar resultado.jpg
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import unicodedata
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

cv2: Any = None
np: Any = None


BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR / "amostras"
MODEL_DIR = BASE_DIR / "modelo"
MODEL_PATH = MODEL_DIR / "faces_lbph.yml"
LABELS_PATH = MODEL_DIR / "labels.json"
PEOPLE_PATH = DATASET_DIR / "pessoas.json"
FACE_SIZE = (160, 160)
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sistema simples de identificacao facial local usando OpenCV LBPH."
    )
    subparsers = parser.add_subparsers(dest="comando", required=True)

    cadastrar = subparsers.add_parser(
        "cadastrar",
        help="Captura amostras de rosto pela camera para uma pessoa autorizada.",
    )
    cadastrar.add_argument("--nome", required=True, help="Nome da pessoa a cadastrar.")
    cadastrar.add_argument(
        "--camera",
        default="0",
        help="Indice da camera, URL de stream ou arquivo de video (padrao: 0).",
    )
    cadastrar.add_argument(
        "--amostras",
        type=int,
        default=40,
        help="Quantidade de amostras a capturar (padrao: 40).",
    )
    cadastrar.add_argument(
        "--intervalo",
        type=float,
        default=0.25,
        help="Intervalo minimo, em segundos, entre amostras salvas (padrao: 0.25).",
    )
    cadastrar.add_argument(
        "--min-rosto",
        type=int,
        default=80,
        help="Tamanho minimo do rosto detectado em pixels (padrao: 80).",
    )

    treinar = subparsers.add_parser(
        "treinar",
        help="Treina o modelo com as amostras salvas em amostras/<pessoa>/.",
    )
    treinar.add_argument(
        "--min-amostras",
        type=int,
        default=10,
        help="Minimo recomendado de imagens por pessoa (padrao: 10).",
    )

    identificar = subparsers.add_parser(
        "identificar",
        help="Identifica rostos cadastrados em uma imagem, camera ou stream.",
    )
    source_group = identificar.add_mutually_exclusive_group()
    source_group.add_argument("--imagem", type=Path, help="Caminho de uma imagem.")
    source_group.add_argument(
        "--camera",
        default="0",
        help="Indice da camera, URL de stream ou arquivo de video (padrao: 0).",
    )
    identificar.add_argument(
        "--limite",
        type=float,
        default=70.0,
        help="Distancia maxima do LBPH para aceitar a identidade (padrao: 70.0).",
    )
    identificar.add_argument(
        "--min-rosto",
        type=int,
        default=80,
        help="Tamanho minimo do rosto detectado em pixels (padrao: 80).",
    )
    identificar.add_argument(
        "--salvar",
        type=Path,
        help="Salva uma imagem anotada no caminho informado.",
    )
    identificar.add_argument(
        "--sem-janela",
        action="store_true",
        help="Nao abre janela grafica ao processar imagem.",
    )

    return parser.parse_args()


def ensure_dirs() -> None:
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)


def require_dependencies() -> None:
    global cv2, np

    if cv2 is not None and np is not None:
        return

    try:
        import cv2 as cv2_module
        import numpy as np_module
    except ImportError as exc:
        raise RuntimeError(
            "Dependencias nao instaladas. Execute: pip install -r requirements.txt"
        ) from exc

    cv2 = cv2_module
    np = np_module


def make_recognizer() -> Any:
    require_dependencies()
    if not hasattr(cv2, "face"):
        raise RuntimeError(
            "O modulo cv2.face nao foi encontrado. Instale com: "
            "pip install opencv-contrib-python"
        )
    return cv2.face.LBPHFaceRecognizer_create(radius=1, neighbors=8, grid_x=8, grid_y=8)


def load_cascade() -> Any:
    require_dependencies()
    cascade_path = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"
    cascade = cv2.CascadeClassifier(str(cascade_path))
    if cascade.empty():
        raise RuntimeError(f"Classificador Haar nao encontrado: {cascade_path}")
    return cascade


def open_video_source(source: str) -> Any:
    require_dependencies()
    if source.isdigit():
        capture = cv2.VideoCapture(int(source))
    else:
        capture = cv2.VideoCapture(source)
    if not capture.isOpened():
        raise RuntimeError(f"Nao foi possivel abrir a fonte de video: {source}")
    return capture


def sanitize_name(name: str) -> str:
    normalized = unicodedata.normalize("NFKD", name.strip())
    normalized = normalized.encode("ascii", "ignore").decode("ascii").lower()
    normalized = re.sub(r"[^a-z0-9_-]+", "_", normalized)
    normalized = re.sub(r"_+", "_", normalized).strip("_")
    if not normalized:
        raise ValueError("Informe um nome com pelo menos uma letra ou numero.")
    return normalized


def load_people() -> Dict[str, str]:
    if not PEOPLE_PATH.exists():
        return {}
    with PEOPLE_PATH.open("r", encoding="utf-8") as people_file:
        data = json.load(people_file)
    return {str(key): str(value) for key, value in data.items()}


def save_people(people: Dict[str, str]) -> None:
    ensure_dirs()
    with PEOPLE_PATH.open("w", encoding="utf-8") as people_file:
        json.dump(people, people_file, indent=2, ensure_ascii=False)
        people_file.write("\n")


def detect_faces(
    gray: Any,
    cascade: Any,
    min_face_size: int,
) -> List[Tuple[int, int, int, int]]:
    faces = cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(min_face_size, min_face_size),
    )
    return sorted(faces, key=lambda box: box[2] * box[3], reverse=True)


def crop_and_normalize(gray: Any, box: Tuple[int, int, int, int]) -> Any:
    x, y, width, height = box
    face = gray[y : y + height, x : x + width]
    face = cv2.resize(face, FACE_SIZE, interpolation=cv2.INTER_AREA)
    return cv2.equalizeHist(face)


def iter_person_dirs() -> Iterable[Path]:
    if not DATASET_DIR.exists():
        return []
    return sorted(path for path in DATASET_DIR.iterdir() if path.is_dir())


def iter_images(person_dir: Path) -> Iterable[Path]:
    return sorted(
        path
        for path in person_dir.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )


def next_sample_path(person_dir: Path, person_id: str) -> Path:
    existing = [
        int(match.group(1))
        for path in iter_images(person_dir)
        if (match := re.search(r"_(\d+)$", path.stem))
    ]
    next_index = max(existing, default=0) + 1
    return person_dir / f"{person_id}_{next_index:04d}.png"


def draw_label(
    frame: Any,
    box: Tuple[int, int, int, int],
    label: str,
    color: Tuple[int, int, int],
) -> None:
    x, y, width, height = box
    cv2.rectangle(frame, (x, y), (x + width, y + height), color, 2)
    (text_width, text_height), _ = cv2.getTextSize(
        label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2
    )
    top = max(y - text_height - 10, 0)
    cv2.rectangle(frame, (x, top), (x + text_width + 8, top + text_height + 8), color, -1)
    cv2.putText(
        frame,
        label,
        (x + 4, top + text_height + 4),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (0, 0, 0),
        2,
        cv2.LINE_AA,
    )


def register_person(args: argparse.Namespace) -> int:
    ensure_dirs()
    person_id = sanitize_name(args.nome)
    person_dir = DATASET_DIR / person_id
    person_dir.mkdir(parents=True, exist_ok=True)

    people = load_people()
    people[person_id] = args.nome.strip()
    save_people(people)

    cascade = load_cascade()
    capture = open_video_source(args.camera)
    saved = 0
    last_saved = 0.0

    print("Cadastro iniciado. Olhe para a camera e varie levemente o angulo do rosto.")
    print("Pressione 'q' para encerrar antes do limite.")

    try:
        while saved < args.amostras:
            ok, frame = capture.read()
            if not ok:
                print("Frame nao recebido da camera.")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detect_faces(gray, cascade, args.min_rosto)
            now = time.monotonic()

            if faces:
                face = faces[0]
                if now - last_saved >= args.intervalo:
                    sample = crop_and_normalize(gray, face)
                    sample_path = next_sample_path(person_dir, person_id)
                    cv2.imwrite(str(sample_path), sample)
                    saved += 1
                    last_saved = now
                    print(f"Amostra salva: {sample_path.name} ({saved}/{args.amostras})")

                draw_label(frame, face, f"{args.nome}: {saved}/{args.amostras}", (0, 255, 0))

            cv2.imshow("Cadastro facial", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        capture.release()
        cv2.destroyAllWindows()

    print(f"Cadastro finalizado. Total de amostras salvas: {saved}")
    return 0 if saved > 0 else 1


def train_model(args: argparse.Namespace) -> int:
    require_dependencies()
    ensure_dirs()
    recognizer = make_recognizer()
    people = load_people()

    samples: List[Any] = []
    labels: List[int] = []
    label_map: Dict[int, str] = {}
    next_label = 0

    for person_dir in iter_person_dirs():
        images = list(iter_images(person_dir))
        if not images:
            continue

        if len(images) < args.min_amostras:
            print(
                f"Aviso: {person_dir.name} possui apenas {len(images)} amostras "
                f"(recomendado: {args.min_amostras})."
            )

        label_map[next_label] = people.get(person_dir.name, person_dir.name)

        for image_path in images:
            image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
            if image is None:
                print(f"Aviso: imagem ignorada por falha de leitura: {image_path}")
                continue
            image = cv2.resize(image, FACE_SIZE, interpolation=cv2.INTER_AREA)
            image = cv2.equalizeHist(image)
            samples.append(image)
            labels.append(next_label)

        next_label += 1

    if not samples:
        print("Nenhuma amostra encontrada. Use o comando 'cadastrar' primeiro.")
        return 1

    recognizer.train(samples, np.array(labels, dtype=np.int32))
    recognizer.write(str(MODEL_PATH))
    with LABELS_PATH.open("w", encoding="utf-8") as labels_file:
        json.dump(label_map, labels_file, indent=2, ensure_ascii=False)
        labels_file.write("\n")

    print(f"Modelo treinado com {len(samples)} amostras de {len(label_map)} pessoa(s).")
    print(f"Modelo salvo em: {MODEL_PATH}")
    return 0


def load_model() -> Tuple[Any, Dict[int, str]]:
    if not MODEL_PATH.exists() or not LABELS_PATH.exists():
        raise RuntimeError("Modelo nao encontrado. Execute: python identificacao_facial.py treinar")

    recognizer = make_recognizer()
    recognizer.read(str(MODEL_PATH))
    with LABELS_PATH.open("r", encoding="utf-8") as labels_file:
        raw_labels = json.load(labels_file)
    labels = {int(label_id): str(name) for label_id, name in raw_labels.items()}
    return recognizer, labels


def annotate_frame(
    frame: Any,
    recognizer: Any,
    labels: Dict[int, str],
    cascade: Any,
    limit: float,
    min_face_size: int,
) -> np.ndarray:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detect_faces(gray, cascade, min_face_size)

    for face in faces:
        sample = crop_and_normalize(gray, face)
        predicted_label, distance = recognizer.predict(sample)
        if distance <= limit:
            name = labels.get(predicted_label, f"ID {predicted_label}")
            text = f"{name} ({distance:.1f})"
            color = (0, 255, 0)
        else:
            text = f"Desconhecido ({distance:.1f})"
            color = (0, 180, 255)
        draw_label(frame, face, text, color)

    cv2.putText(
        frame,
        f"Rostos: {len(faces)}",
        (10, 28),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )
    return frame


def identify_image(args: argparse.Namespace) -> int:
    recognizer, labels = load_model()
    cascade = load_cascade()

    frame = cv2.imread(str(args.imagem))
    if frame is None:
        print(f"Nao foi possivel abrir a imagem: {args.imagem}")
        return 1

    annotated = annotate_frame(
        frame,
        recognizer,
        labels,
        cascade,
        args.limite,
        args.min_rosto,
    )

    if args.salvar:
        args.salvar.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(args.salvar), annotated)
        print(f"Imagem anotada salva em: {args.salvar}")

    if not args.sem_janela:
        cv2.imshow("Identificacao facial", annotated)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return 0


def identify_video(args: argparse.Namespace) -> int:
    recognizer, labels = load_model()
    cascade = load_cascade()
    capture = open_video_source(args.camera)

    print("Identificacao iniciada. Pressione 'q' para sair.")
    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                print("Frame nao recebido da camera/stream.")
                break

            annotated = annotate_frame(
                frame,
                recognizer,
                labels,
                cascade,
                args.limite,
                args.min_rosto,
            )

            cv2.imshow("Identificacao facial", annotated)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        capture.release()
        cv2.destroyAllWindows()

    return 0


def identify(args: argparse.Namespace) -> int:
    if args.imagem:
        return identify_image(args)
    return identify_video(args)


def main() -> int:
    args = parse_args()
    try:
        if args.comando == "cadastrar":
            return register_person(args)
        if args.comando == "treinar":
            return train_model(args)
        if args.comando == "identificar":
            return identify(args)
    except KeyboardInterrupt:
        print("\nOperacao interrompida pelo usuario.")
        return 130
    except Exception as exc:
        print(f"Erro: {exc}")
        return 1

    print(f"Comando desconhecido: {args.comando}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
