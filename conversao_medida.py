import csv
import cv2
import os
import numpy as np
import matplotlib.pyplot as plt

# Função para detectar linhas verticais em uma imagem e retornar a altura máxima dessas linhas
def detectar_retas_verticais_e_altura(image_path):
    # Carregar a imagem a partir do caminho fornecido
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Aplicar desfoque GaussianBlur para suavização e redução de ruídos
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Detectar bordas usando o algoritmo Canny
    edges = cv2.Canny(blurred, 50, 150)

    # Criar um kernel para operações morfológicas que destacam linhas verticais
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 20))
    vertical_lines = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    # Detectar linhas verticais utilizando a Transformada de Hough
    lines = cv2.HoughLinesP(vertical_lines, 1, np.pi / 180, threshold=80, minLineLength=50, maxLineGap=10)

    # Criar uma cópia da imagem original para desenhar as linhas detectadas
    output_image = image.copy()

    # Verificar se linhas foram detectadas
    if lines is not None:
        alturas = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(output_image, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Desenhar linha na cópia da imagem
            altura = abs(y2 - y1)  # Calcular a altura da linha
            alturas.append(altura)
        return max(alturas)  # Retornar a maior altura encontrada

    # Exibir a imagem original e a imagem com linhas verticais detectadas
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.title("Imagem Original")
    plt.axis("off")

    plt.subplot(1, 2, 2)
    plt.imshow(cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB))
    plt.title("Linhas Verticais Detectadas")
    plt.axis("off")

    plt.show()

# Definir o diretório onde serão salvos os cortes das imagens
output_dir = '/content/gdrive/MyDrive/facul/Graph/Imagens_testes/Cortes'
os.makedirs(output_dir, exist_ok=True)  # Criar o diretório se não existir

# Caminho para o arquivo CSV onde serão salvos os resultados
output_csv = os.path.join(output_dir, 'resultados.csv')

# Abrir o arquivo CSV no modo de escrita
with open(output_csv, mode='w', newline='') as file:
    writer = csv.writer(file)
    # Escrever o cabeçalho do CSV
    writer.writerow(['Imagem', 'Classe', 'Confiança', 'x1', 'y1', 'x2', 'y2', 'altura', 'largura', 'altura_max', 'largura_max'])

    # Iterar sobre cada caminho de imagem para processamento
    for image_path in image_paths:
        # Aqui deveria ter a definição do modelo, mas está faltando no código fornecido
        results = model(image_path)  # Processar a imagem com o modelo de detecção

        # Carregar a imagem original para obter suas dimensões
        image = cv2.imread(image_path)
        altura_max, largura_max, _ = image.shape

        # Iterar sobre cada detecção encontrada na imagem
        for idx, detection in enumerate(results[0].boxes):
            bbox = detection.xyxy[0].cpu().numpy()  # Obter as coordenadas da caixa delimitadora
            confidence = detection.conf[0].cpu().numpy()  # Obter a confiança da detecção
            class_id = int(detection.cls[0].cpu().numpy())  # Obter o ID da classe detectada

            # Exibir informações sobre a detecção no console
            print(f"Imagem: {image_path}, Classe: {class_id}, Confiança: {confidence}, Coordenadas: {bbox}")

            # Converter as coordenadas da caixa delimitadora para inteiros
            x1, y1, x2, y2 = map(int, bbox)

            # Verificar se a detecção é da classe ID 1 para salvar o corte
            if class_id == 1:
                # Garantir que as coordenadas estão dentro dos limites da imagem
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(largura_max, x2), min(altura_max, y2)

                # Cortar a região da imagem correspondente à detecção
                cropped_image = image[y1:y2, x1:x2]

                # Salvar o corte com um nome de arquivo único baseado no nome original e ID da classe
                base_name = os.path.basename(image_path).split('.')[0]
                output_path = os.path.join(output_dir, f"{base_name}_id1_corte_{idx}.png")
                cv2.imwrite(output_path, cropped_image)

                # Obter as dimensões do corte
                altura, largura, _ = cropped_image.shape

                # Escrever os resultados da detecção e dimensões no CSV
                writer.writerow([image_path, class_id, confidence, *bbox, altura, largura, altura_max, largura_max])

                print(f"Corte salvo em: {output_path}")

            # Repetir o mesmo processo para a classe ID 0
            if class_id == 0:
                # Garantir que as coordenadas estão dentro dos limites da imagem
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(largura_max, x2), min(altura_max, y2)

                # Cortar a região da imagem correspondente à detecção
                cropped_image = image[y1:y2, x1:x2]

                # Salvar o corte com um nome de arquivo único baseado no nome original e ID da classe
                base_name = os.path.basename(image_path).split('.')[0]
                output_path = os.path.join(output_dir, f"{base_name}_id0_corte_{idx}.png")
                cv2.imwrite(output_path, cropped_image)

                # Obter as dimensões do corte
                altura, largura, _ = cropped_image.shape

                # Escrever os resultados da detecção e dimensões no CSV
                writer.writerow([image_path, class_id, confidence, *bbox, altura, largura, altura_max, largura_max])

                print(f"Corte salvo em: {output_path}")

# Supor que 'image_paths' é uma lista gerada pelo 'glob.glob' com caminhos para as imagens .png
# Aqui está faltando a definição da variável 'image_paths' e do modelo 'model', que deveriam ter sido definidas anteriormente

# Iterar sobre cada caminho de imagem para verificar se existe e para detectar linhas verticais
for image_path in image_paths:
    if os.path.exists(image_path):
        print("Imagem encontrada.")
        detectar_retas_verticais_e_altura(image_path)
    else:
        print("Imagem NÃO encontrada no caminho especificado.")

# Informar ao usuário onde o arquivo CSV com os resultados foi salvo
print(f"Resultados salvos no CSV: {output_csv}")
