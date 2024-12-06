import os
from pathlib import Path
import concurrent.futures
import time
from tqdm import tqdm
from PIL import Image
from pillow_heif import register_heif_opener
from wand.image import Image as WandImage
from wand.color import Color

# Registra o suporte a HEIF/HEIC no Pillow
register_heif_opener()

def convert_heic_to_png(input_path, output_path):
    """
    Converte um arquivo HEIC para PNG usando Pillow.
    
    Args:
        input_path (str): Caminho do arquivo HEIC
        output_path (str): Caminho para salvar o arquivo PNG
    """
    try:
        with Image.open(input_path) as img:
            # Preserva a qualidade máxima na conversão
            img.save(output_path, 'PNG', optimize=True)
        return True
    except Exception as e:
        print(f"Erro ao converter {input_path}: {str(e)}")
        return False

def convert_cr2_to_png(input_path, output_path):
    """
    Converte um arquivo CR2 para PNG usando Wand/ImageMagick.
    
    Args:
        input_path (str): Caminho do arquivo CR2
        output_path (str): Caminho para salvar o arquivo PNG
    """
    try:
        with WandImage(filename=input_path) as img:
            # Ajusta os parâmetros da imagem
            img.format = 'png'
            img.compression_quality = 90
            
            # Remove canal alpha se existir
            if img.alpha_channel:
                img.alpha_channel = 'remove'
            
            # Salva como PNG
            img.save(filename=output_path)
        return True
    except Exception as e:
        print(f"Erro ao converter {input_path}: {str(e)}")
        return False

def process_directory(input_dir, output_dir, conversion_type, max_workers=4):
    """
    Processa todos os arquivos HEIC ou CR2 em um diretório.
    
    Args:
        input_dir (str): Diretório com os arquivos HEIC ou CR2
        output_dir (str): Diretório para salvar os arquivos PNG
        conversion_type (str): Tipo de conversão ('HEIC' ou 'CR2')
        max_workers (int): Número máximo de threads para processamento paralelo
    """
    # Cria o diretório de saída se não existir
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Define as extensões de arquivo com base no tipo de conversão
    extensions = ['.heic', '.HEIC', '.heif', '.HEIF'] if conversion_type == 'HEIC' else ['.cr2', '.CR2']
    
    # Lista todos os arquivos com as extensões especificadas
    files = []
    for ext in extensions:
        files.extend(list(Path(input_dir).glob(f'**/*{ext}')))
    
    if not files:
        print(f"Nenhum arquivo {conversion_type} encontrado!")
        return
    
    print(f"Encontrados {len(files)} arquivos {conversion_type}")
    
    # Prepara as tarefas de conversão
    conversion_tasks = []
    for file_path in files:
        # Mantém a estrutura de diretórios relativa
        relative_path = file_path.relative_to(input_dir)
        output_path = Path(output_dir) / relative_path.with_suffix('.png')
        
        # Cria os subdiretórios necessários
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        conversion_tasks.append((str(file_path), str(output_path)))
    
    # Define a função de conversão com base no tipo de conversão
    conversion_func = convert_heic_to_png if conversion_type == 'HEIC' else convert_cr2_to_png
    
    # Processa as conversões em paralelo com barra de progresso
    successful = 0
    failed = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(conversion_func, input_path, output_path): (input_path, output_path) 
                  for input_path, output_path in conversion_tasks}
        
        with tqdm(total=len(conversion_tasks), desc="Convertendo imagens") as pbar:
            for future in concurrent.futures.as_completed(futures):
                success = future.result()
                if success:
                    successful += 1
                else:
                    failed += 1
                pbar.update(1)
    
    print(f"\nConversão concluída!")
    print(f"Convertidas com sucesso: {successful}")
    print(f"Falhas na conversão: {failed}")

if __name__ == "__main__":
    # Solicita o tipo de conversão
    while True:
        conversion_type = input("Digite o tipo de conversão (HEIC ou CR2): ")
        if conversion_type.upper() in ['HEIC', 'CR2']:
            break
        print("Tipo de conversão inválido. Por favor, digite 'HEIC' ou 'CR2'.")
    
    # Solicita o caminho de origem
    while True:
        input_dir = input("Digite o caminho de origem dos arquivos: ")
        if Path(input_dir).exists():
            break
        print("Caminho de origem inválido. Por favor, digite um caminho válido.")
    
    # Solicita o caminho de destino
    while True:
        output_dir = input("Digite o caminho de destino para salvar os arquivos convertidos: ")
        if Path(output_dir).parent.exists():
            break
        print("Caminho de destino inválido. Por favor, digite um caminho válido.")
    
    # Exibe o alerta de confirmação
    print("\nConfirmação:")
    print(f"Tipo de conversão: {conversion_type}")
    print(f"Caminho de origem: {input_dir}")
    print(f"Caminho de destino: {output_dir}")
    confirmation = input("Deseja prosseguir com a conversão? (S/N): ")
    
    if confirmation.upper() == 'S':
        # Configurações
        MAX_WORKERS = 16  # Número de threads para processamento paralelo
        
        # Registra o tempo de início
        start_time = time.time()
        
        # Executa o processamento
        process_directory(input_dir, output_dir, conversion_type.upper(), MAX_WORKERS)
        
        # Calcula e exibe o tempo total
        elapsed_time = time.time() - start_time
        print(f"\nTempo total de processamento: {elapsed_time:.2f} segundos")
    else:
        print("Conversão cancelada pelo usuário.")