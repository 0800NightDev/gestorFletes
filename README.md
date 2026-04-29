<div align="center">
  <img src="svg/logo_letras.svg" alt="Alexander Moya Fleet System Logo" width="400">
</div>

# Alexander Moya Fleet System (Gestor de Fletes)

<div align="center">
  <img src="svg/logo_clean.svg" alt="App Icon" width="120">
</div>

## 🏢 Sobre la Empresa y el Software

**Alexander Moya Fleet System** es una solución corporativa de alto rendimiento para el seguimiento logístico y la gestión de flotas de transporte. Desarrollado para optimizar la eficiencia operativa, este software de escritorio permite a las empresas de transporte administrar su parque automotor, asignar viajes de carga y supervisar en tiempo real la telemetría de cada unidad mediante una interfaz gráfica moderna, profesional y altamente responsiva.

El sistema fusiona el control de datos centralizado con simulaciones en tiempo real para crear un ecosistema de gestión total, permitiendo generar reportes, validar métricas de rendimiento y administrar de manera unificada toda la logística del ciclo de vida del flete.

## 🚀 Funcionamiento y Características Principales

El sistema está dividido en varios módulos que interactúan entre sí de forma transparente:

- **Dashboard Principal:** Panel de telemetría y control general. Permite visualizar el estado en tiempo real de los vehículos (Velocidad, Combustible, RPM, Temperatura) apoyado por indicadores visuales (Circular Gauges) de precisión.
- **Gestión de Camiones:** Interfaz para registrar, editar y administrar el parque automotor de la empresa, incluyendo datos de la placa, modelo, conductor asignado, seriales y alertas de mantenimiento según el kilometraje.
- **Simulación de Telemetría (Real-Time):** Motor interno que simula los sensores físicos del camión (fluctuaciones de combustible, aceleración, alertas por exceso de velocidad) para brindar una experiencia de monitoreo en tiempo real.
- **Validación de Fletes (Freight Validator):** Sistema robusto para verificar y asegurar que las asignaciones de carga cumplan con todos los requisitos operativos antes de autorizar la salida de un camión.
- **Módulo de Reportes:** Generación automática de reportes de auditoría y análisis de la flota listos para la toma de decisiones gerenciales.

## 🏗️ Arquitectura del Sistema

El proyecto está diseñado bajo un modelo estructurado **MVC (Model-View-Controller)** para asegurar la mantenibilidad y escalabilidad del código. Está programado completamente en **Python 3** y utiliza la última tecnología de interfaces gráficas.

* **Frontend / GUI (Views):** Construido usando **PyQt6**, con un diseño corporativo moderno ("Dark Mode") potenciado por **qt-material**. Implementa componentes personalizados como `circular_gauge.py` y paneles dinámicos fluidos.
* **Backend / Lógica de Negocio (Core):**
  * `telemetry_simulator.py`: Hilos en segundo plano (`QThread`) para la inyección asíncrona de datos de sensores en tiempo real sin bloquear la interfaz.
  * `freight_validator.py`: Lógica algorítmica para la verificación de integridad de los fletes.
* **Capa de Datos (Models):**
  * `db_manager.py`: Controlador transaccional que utiliza **SQLite3** con un `schema.sql` robusto para persistencia de datos local, asegurando la sincronización de vehículos y métricas operacionales.
* **Distribución (CI/CD):**
  * Empaquetado automático con **PyInstaller** e integración continua a través de **GitHub Actions** (`windows_build.yml`) que compila la aplicación a un archivo `.exe` nativo de Windows listo para su descarga y ejecución sin dependencias de Python instaladas.

## 🛠️ Requisitos de Desarrollo

- Python 3.11+
- PyQt6
- qt-material

Para instalar las dependencias localmente, ejecuta:
```bash
pip install -r requirements.txt
```

Para iniciar el sistema en entorno de desarrollo:
```bash
python main.py
```
