import os
from pathlib import Path
import concurrent.futures
import time
from tqdm import tqdm
from PIL import Image
from pillow_heif import register_heif_opener

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

def process_directory(input_dir, output_dir, max_workers=4):
    """
    Processa todos os arquivos HEIC em um diretório.
    
    Args:
        input_dir (str): Diretório com os arquivos HEIC
        output_dir (str): Diretório para salvar os arquivos PNG
        max_workers (int): Número máximo de threads para processamento paralelo
    """
    # Cria o diretório de saída se não existir
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Lista todos os arquivos HEIC (considerando maiúsculas e minúsculas)
    heic_files = []
    for ext in ['.heic', '.HEIC', '.heif', '.HEIF']:
        heic_files.extend(list(Path(input_dir).glob(f'**/*{ext}')))
    
    if not heic_files:
        print("Nenhum arquivo HEIC/HEIF encontrado!")
        return
    
    print(f"Encontrados {len(heic_files)} arquivos HEIC/HEIF")
    
    # Prepara as tarefas de conversão
    conversion_tasks = []
    for heic_path in heic_files:
        # Mantém a estrutura de diretórios relativa
        relative_path = heic_path.relative_to(input_dir)
        output_path = Path(output_dir) / relative_path.with_suffix('.png')
        
        # Cria os subdiretórios necessários
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        conversion_tasks.append((str(heic_path), str(output_path)))
    
    # Processa as conversões em paralelo com barra de progresso
    successful = 0
    failed = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(convert_heic_to_png, input_path, output_path): (input_path, output_path) 
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
    # Configurações
    INPUT_DIR = r"C:\Users\Guilherme-PC\Desktop\Converter"  # Altere para o seu diretório de entrada
    OUTPUT_DIR = r"C:\Users\Guilherme-PC\Desktop\Convertido"  # Altere para o seu diretório de saída
    MAX_WORKERS = 14  # Número de threads para processamento paralelo
    
    # Registra o tempo de início
    start_time = time.time()
    
    # Executa o processamento
    process_directory(INPUT_DIR, OUTPUT_DIR, MAX_WORKERS)
    
    # Calcula e exibe o tempo total
    elapsed_time = time.time() - start_time
    print(f"\nTempo total de processamento: {elapsed_time:.2f} segundos")