# Imagen base para AWS Lambda Python
# La imagen public.ecr.aws/lambda/python:3.11 incluye:
#    LAMBDA_TASK_ROOT=/var/task
#    LAMBDA_RUNTIME_DIR=/var/runtime
#    Otras variables de entorno de Lambda
FROM public.ecr.aws/lambda/python:3.11

# Copiar archivos de dependencias
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY main.py ${LAMBDA_TASK_ROOT}
COPY lambda_function.py ${LAMBDA_TASK_ROOT}

# Configurar el handler de Lambda
CMD ["lambda_function.lambda_handler"]
