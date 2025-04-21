import boto3
from botocore.exceptions import ClientError
from datetime import datetime
import json

# Inicializa clientes
ec2 = boto3.client('ec2')
s3 = boto3.client('s3')

# --- 1. Verificar instancias EC2 existentes ---
def contar_instancias_ec2():
    response = ec2.describe_instances()
    count = 0
    for res in response['Reservations']:
        count += len(res['Instances'])
    return count

# --- 2. Crear nuevas instancias (máx 9) ---
def crear_instancias_ec2(cantidad):
    ami_id = 'ami-0c02fb55956c7d316'  # Amazon Linux 2 AMI (us-east-1)
    instancia_tipo = 't2.micro'
    
    try:
        response = ec2.run_instances(
            ImageId=ami_id,
            InstanceType=instancia_tipo,
            MinCount=1,
            MaxCount=cantidad,
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [{'Key': 'Proyecto', 'Value': 'AutoScript'}]
                }
            ]
        )
        ids = [inst['InstanceId'] for inst in response['Instances']]
        print(f"Instancias creadas: {ids}")
        return ids
    except ClientError as e:
        print("Error al crear instancias:", e)

# --- 3. Listar buckets y sus objetos ---
def listar_buckets_y_objetos():
    buckets_info = []
    response = s3.list_buckets()
    for bucket in response['Buckets']:
        nombre = bucket['Name']
        print(f"\nBucket: {nombre}")
        try:
            objetos = s3.list_objects_v2(Bucket=nombre)
            objetos_lista = [obj['Key'] for obj in objetos.get('Contents', [])]
            buckets_info.append({'Bucket': nombre, 'Objetos': objetos_lista})
        except ClientError as e:
            print(f"No se pudo acceder a objetos del bucket {nombre}: {e}")
            buckets_info.append({'Bucket': nombre, 'Objetos': []})
    return buckets_info

# --- 4. Generar reporte de uso de recursos ---
def generar_reporte(instancias_creadas, buckets_info):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    reporte = {
        "Fecha": timestamp,
        "InstanciasEC2_Creadas": instancias_creadas,
        "Buckets_S3": buckets_info
    }
    nombre_archivo = f"reporte_aws_{timestamp}.json"
    with open(nombre_archivo, 'w') as f:
        json.dump(reporte, f, indent=4)
    print(f"\n📄 Reporte generado: {nombre_archivo}")

# --- MAIN ---
if __name__ == "__main__":
    print("⏳ Consultando número de instancias EC2...")
    total_actual = contar_instancias_ec2()
    print(f"📌 Instancias actuales: {total_actual}")
    
    if total_actual < 9:
        cantidad_nuevas = 9 - total_actual
        print(f"🚀 Creando {cantidad_nuevas} instancias EC2...")
        nuevas = crear_instancias_ec2(cantidad_nuevas)
    else:
        print("✅ Ya hay 9 o más instancias, no se crean más.")
        nuevas = []

    print("\n🔍 Listando buckets S3 y objetos...")
    buckets = listar_buckets_y_objetos()

    print("\n📝 Generando reporte...")
    generar_reporte(nuevas, buckets)
