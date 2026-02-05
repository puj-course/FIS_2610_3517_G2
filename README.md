# Gruver 🚚

## ![logo Gruver](https://github.com/user-attachments/assets/f358b1f9-c165-4f42-ae82-2853da9c6074)


## Propuesta de Valor y Diferenciador

### ¿Por qué usar Gruber?
- Disminuye los tiempos de respuesta en la solicitud de grúas, evitando pérdidas económicas por la inmovilización de vehículos.
- Aumenta la productividad y la satisfacción del cliente final de las aseguradoras.

### Beneficio principal
- Optimización del proceso de solicitud de grúas mediante flujos digitales, eliminando la dependencia de múltiples llamadas telefónicas y gestiones manuales dispersas.

### Diferenciador
- Solución centrada en **software y aplicación móvil**, sin depender de call centers extensos.
- Enfoque visual tipo **Uber**, orientado a rapidez y claridad en la gestión de siniestros.

---

## Información General del Proyecto

| **Elemento** | **Detalle** |
| --- | --- |
| **Nombre** | Gruber |
| **Propuesta** | Servicio de grúas en minutos vía aplicación, orientado a empresas y aseguradoras |
| **Usuarios** | Aseguradoras y empresas (clientes directos); usuarios finales a través de la cobertura del seguro |
| **Interfaz** | Mapa tipo Uber con grúas simuladas y flujo básico de solicitud |
| **Entregables** | Presentación PDF, Lean Canvas, README, documentación/wiki y boilerplate en GitHub |

---

## Roles y Responsabilidades del Equipo

### 🧑‍💼 Project Manager / Scrum Master – John Rubio
- Coordinación de reuniones y comunicación con el profesor (cliente).
- Distribución de tareas semanales.
- Apoyo transversal a backend, frontend y QA.

### 🧠 Backend Developer – Juan Pablo Álvarez
- Diseño e implementación de la lógica principal del sistema.
- Desarrollo de la capa de persistencia.
- Exposición de datos al frontend mediante servicios.

### 🎨 Frontend Developer – Nicolás Sánchez
- Diseño y construcción de la interfaz de usuario.
- Implementación del mapa, formularios y vistas principales.
- Integración del logo y lineamientos visuales de la marca Gruber.

### 📝 Documentador / Repo Manager – Lucas Rincón
- Redacción y mantenimiento de la documentación del proyecto.
- Organización de la wiki o carpeta `/docs`.
- Actualización del repositorio con entregables y diagramas.

### 🧪 Tester / QA – David Orjuela
- Definición y ejecución de pruebas funcionales y de persistencia.
- Validación del cumplimiento de requisitos.
- Apoyo en la detección y corrección de errores.

---

## Descripción y Alcance del Proyecto

### Descripción
**Gruber** es una startup ficticia orientada a ofrecer a **empresas y aseguradoras** una solución de software que permita solicitar servicios de grúa en tiempo récord, reduciendo tiempos muertos y pérdidas económicas asociadas a siniestros o fallas vehiculares.

### Tipo de problema
- Organizacional y de productividad.
- Procesos actuales lentos, manuales y poco centralizados.

### Público objetivo
- **Directo:** aseguradoras y empresas que gestionan flotas o siniestros.
- **Indirecto:** usuarios finales que acceden al servicio mediante su aseguradora.

---

## Alcance Funcional de la Demo

- Aplicación con interfaz de mapa tipo Uber.
- Visualización de grúas disponibles de forma simulada.
- Registro de solicitudes de grúa desde un origen hasta un destino.
- Simulación de disponibilidad de grúas mediante lógica simple o generación aleatoria.

### Simulación
- No existe conexión con grúas reales.
- Las posiciones y estados de las grúas son simulados.
- La simulación es coherente con el flujo funcional explicado en la presentación del proyecto.

---

## Materia

**Fundamentos de Desarrollo de Software**  
Proyecto académico desarrollado como parte del curso.

# fis_boilerplate
## Descripción de cada directorio y archivos
```bash
project-name/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   ├── feature_request.md
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/
│       ├── ci.yml
│       └── cd.yml
├── conf/
│   ├── config.yaml
│   └── settings.json
├── docs/
│   ├── api/
│   ├── architecture/
│   └── user_guide/
├── jupyter/
│   ├── notebooks/
│   │   ├── exploration.ipynb
│   │   └── analysis.ipynb
│   └── datasets/
│       ├── data1.csv
│       └── data2.csv
├── scripts/
│   ├── setup.sh
│   ├── deploy.sh
│   └── test.sh
├── src/
│   ├── main/
│   │   ├── java/ (o python/, etc. según el lenguaje)
│   │   └── resources/
│   ├── test/
│   │   ├── java/ (o python/, etc. según el lenguaje)
│   │   └── resources/
├── temp/
│   ├── temp_file.txt
│   └── temp_data/
│       ├── temp1.tmp
│       └── temp2.tmp
├── .gitignore
├── README.md
├── LICENSE
├── CHANGELOG.md
├── CONTRIBUTING.md
├── Dockerfile
├── docker-compose.yml
└── Makefile
```


### .github/
Contiene configuraciones específicas para GitHub, como plantillas para problemas (issues) y solicitudes de extracción (pull requests), y flujos de trabajo de GitHub Actions para integración continua (CI) y despliegue continuo (CD).

- `ISSUE_TEMPLATE/`: Plantillas para reportar bugs y solicitar nuevas características.
- `workflows/`: Archivos YAML para definir los flujos de trabajo de CI/CD.

### docs/
Documentación del proyecto.

- `api/`: Documentación de la API.
- `architecture/`: Diagramas y documentación de la arquitectura.
- `user_guide/`: Guías para usuarios.

### src/
Código fuente del proyecto.

- `main/`: Código fuente principal.
  - `java/` (o `python/`, etc.): Código fuente del proyecto según el lenguaje utilizado.
  - `resources/`: Archivos de recursos como configuraciones y otros archivos necesarios.
- `test/`: Código de pruebas.
  - `java/` (o `python/`, etc.): Código de pruebas unitarias y de integración.
  - `resources/`: Archivos de recursos para las pruebas.

### scripts/
Scripts útiles para tareas comunes como configuración, despliegue y pruebas.

- `setup.sh`: Script para configurar el entorno de desarrollo.
- `deploy.sh`: Script para despliegue.
- `test.sh`: Script para ejecutar pruebas.

### conf/
Carpeta para archivos de configuración.

- `config.yaml`: Archivo de configuración en formato YAML.
- `settings.json`: Archivo de configuración en formato JSON.

### jupyter/
Carpeta para los notebooks de Jupyter y datasets utilizados.

- `notebooks/`: Carpeta para los notebooks de Jupyter.
  - `exploration.ipynb`: Notebook para la exploración de datos.
  - `analysis.ipynb`: Notebook para el análisis de datos.
- `datasets/`: Carpeta para los datasets utilizados en los notebooks.
  - `data1.csv`: Ejemplo de dataset en formato CSV.
  - `data2.csv`: Otro ejemplo de dataset en formato CSV.

### temp/
Carpeta para archivos temporales.

- `temp_file.txt`: Archivo temporal de ejemplo.
- `temp_data/`: Subcarpeta para datos temporales.
  - `temp1.tmp`: Archivo temporal de ejemplo.
  - `temp2.tmp`: Otro archivo temporal de ejemplo.

### Archivos en la raíz del proyecto

- `.gitignore`: Archivo para especificar qué archivos y directorios deben ser ignorados por Git.
- `README.md`: Descripción general del proyecto, instrucciones de instalación, uso, contribución, etc.
- `LICENSE`: Información sobre la licencia del proyecto.
- `CHANGELOG.md`: Registro de cambios en el proyecto.
- `CONTRIBUTING.md`: Guía para contribuir al proyecto.
- `Dockerfile`: Archivo para construir la imagen Docker del proyecto.
- `docker-compose.yml`: Archivo de configuración para Docker Compose.
- `Makefile`: Archivo para automatizar tareas mediante comandos `make`.
