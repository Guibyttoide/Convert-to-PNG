import os
os.environ['MAGICK_HOME'] = r"C:\Program Files\ImageMagick-7.1.1-Q16"
os.environ['PATH'] += ';' + os.environ['MAGICK_HOME']
from pathlib import Path
import concurrent.futures
import time
from tqdm import tqdm
from wand.image import Image
from wand.color import Color

def convert_cr2_to_png(input_path, output_path):
    """
    Converte um arquivo CR2 para PNG usando Wand/ImageMagick.
    
    Args:
        input_path (str): Caminho do arquivo CR2
        output_path (str): Caminho para salvar o arquivo PNG
    """
    try:
        with Image(filename=input_path) as img:
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

def process_directory(input_dir, output_dir, max_workers=4):
    """
    Processa todos os arquivos CR2 em um diretório.
    
    Args:
        input_dir (str): Diretório com os arquivos CR2
        output_dir (str): Diretório para salvar os arquivos PNG
        max_workers (int): Número máximo de threads para processamento paralelo
    """
    # Cria o diretório de saída se não existir
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Lista todos os arquivos CR2
    cr2_files = list(Path(input_dir).glob('**/*.CR2'))
    cr2_files.extend(list(Path(input_dir).glob('**/*.cr2')))
    
    if not cr2_files:
        print("Nenhum arquivo CR2 encontrado!")
        return
    
    print(f"Encontrados {len(cr2_files)} arquivos CR2")
    
    # Prepara as tarefas de conversão
    conversion_tasks = []
    for cr2_path in cr2_files:
        # Mantém a estrutura de diretórios relativa
        relative_path = cr2_path.relative_to(input_dir)
        output_path = Path(output_dir) / relative_path.with_suffix('.png')
        
        # Cria os subdiretórios necessários
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        conversion_tasks.append((str(cr2_path), str(output_path)))
    
    # Processa as conversões em paralelo com barra de progresso
    successful = 0
    failed = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(convert_cr2_to_png, input_path, output_path): (input_path, output_path) 
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
    OUTPUT_DIR = r"C:\Users\Guilherme-PC\Desktop\Convertido"        # Altere para o seu diretório de saída
    MAX_WORKERS = 16  # Número de threads para processamento paralelo
    
    # Registra o tempo de início
    start_time = time.time()
    
    # Executa o processamento
    process_directory(INPUT_DIR, OUTPUT_DIR, MAX_WORKERS)
    
    # Calcula e exibe o tempo total
    elapsed_time = time.time() - start_time
    print(f"\nTempo total de processamento: {elapsed_time:.2f} segundos")