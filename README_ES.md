[English](README.md) | [中文](README_CN.md) | [한국어](README_KO.md) | [日本語](README_JP.md) | [Français](README_FR.md) | [Deutsch](README_DE.md) | [Español](README_ES.md)

<img width="3836" height="2026" alt="image" src="https://github.com/user-attachments/assets/d86c3d6b-6fd4-4cfe-b64f-67c465bb3d3c" /><img width="3832" height="2024" alt="image" src="https://github.com/user-attachments/assets/a91d2b13-07ac-4cae-ab33-506f1fa3bca6" />

# Everything by mdfind

Una herramienta de búsqueda de archivos potente y eficiente para macOS, que aprovecha el motor nativo Spotlight para obtener resultados ultrarrápidos.

## Características principales

*   **Búsqueda ultrarrápida:** Utiliza el índice Spotlight de macOS para una búsqueda de archivos casi instantánea.
*   **Opciones de búsqueda flexibles:** Busque por nombre de archivo o contenido para localizar rápidamente los archivos que necesita.
*   **Filtrado avanzado:** Refine sus búsquedas con una variedad de filtros:
    *   Rango de tamaño de archivo (tamaño mínimo y máximo en bytes)
    *   Extensiones de archivo específicas (por ejemplo, `pdf`, `docx`)
    *   Coincidencia que distingue entre mayúsculas y minúsculas
    *   Opciones de coincidencia completa o parcial
*   **Búsqueda específica de directorio:** Limite su búsqueda a un directorio específico para obtener resultados enfocados.
*   **Vista previa enriquecida:** Previsualice varios tipos de archivos directamente en la aplicación:
    *   Archivos de texto con detección de codificación
    *   Imágenes (JPEG, PNG, GIF con soporte de animación, BMP, WEBP, HEIC)
    *   Archivos SVG con escalado y centrado adecuados
    *   Archivos de video con controles de reproducción
    *   Archivos de audio
*   **Reproductor multimedia integrado:**
    *   Reproducción de video y audio con controles estándar
    *   Ventana de reproductor independiente para archivos multimedia
    *   Modo de reproducción continua
    *   Control de volumen y opción de silencio
*   **Marcadores:** Acceso rápido a búsquedas comunes:
    *   Archivos grandes (>50 MB)
    *   Archivos de video
    *   Archivos de audio
    *   Imágenes
    *   Archivos comprimidos
    *   Aplicaciones
*   **Análisis de espacio en disco:** Analice el uso del espacio en disco para cualquier directorio:
    *   Análisis de espacio del directorio de inicio con un clic
    *   Visualización de gráfico de barras interactivo que muestra las carpetas que más espacio consumen
    *   Haga clic derecho en cualquier carpeta de los resultados de búsqueda para analizar su uso de espacio
    *   Desglose visual de los tamaños de subdirectorios con gráficos codificados por colores
    *   Ordenación automática por tamaño para identificar las carpetas más grandes
*   **Resultados ordenables:** Organice los resultados de búsqueda por nombre, tamaño, fecha de modificación o ruta.
*   **Operaciones con múltiples archivos:** Realice acciones en varios archivos simultáneamente:
    *   Seleccione varios archivos usando las teclas Shift o Command (⌘)
    *   Operaciones por lotes: Abrir, Eliminar, Copiar, Mover, Renombrar
    *   Menú contextual para operaciones adicionales
*   **Interfaz de búsqueda con pestañas múltiples:** Trabaje con varias sesiones de búsqueda simultáneamente:
    *   Cree nuevas pestañas para diferentes consultas de búsqueda
    *   Cierre, reorganice y gestione pestañas con el menú contextual del clic derecho
    *   Resultados de búsqueda y configuraciones independientes por pestaña
    *   Experiencia de pestañas similar a Chrome con botones de desplazamiento para muchas pestañas
*   **Interfaz personalizable:**
    *   6 hermosos temas para elegir:
        *   Claro y Oscuro (predeterminado del sistema)
        *   Tokyo Night y Tokyo Night Storm
        *   Chinolor Dark y Chinolor Light (colores tradicionales chinos)
    *   Tematización de la barra de título del sistema que coincide con su tema seleccionado
    *   Mostrar/ocultar panel de vista previa
    *   Historial de búsqueda configurable
*   **Exportación multiformato:** Exporte los resultados de búsqueda a múltiples formatos:
    *   JSON - Formato de datos estructurados
    *   Excel (.xlsx) - Hoja de cálculo con formato
    *   HTML - Formato de tabla listo para web
    *   Markdown - Formato compatible con documentación
    *   CSV - Formato clásico de valores separados por comas
*   **Carga diferida:** Maneja conjuntos de resultados grandes de manera eficiente cargando elementos en lotes a medida que se desplaza.
*   **Arrastrar y soltar:** Arrastre archivos directamente a aplicaciones externas.
*   **Operaciones de ruta:** Copie la ruta del archivo, la ruta del directorio o el nombre del archivo al portapapeles.

## Instalación

1.  **Requisitos previos:**
    *   Python 3.6+
    *   PyQt6

2.  **Clonar el repositorio:**

    ```bash
    git clone https://github.com/appledragon/everythingByMdfind
    cd everythingByMdfind
    ```

3.  **Instalar dependencias:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Ejecutar la aplicación:**

    ```bash
    python everything.py
    ```

## Descargar aplicación precompilada

Puede descargar la aplicación macOS lista para usar (.dmg) directamente desde la página de [GitHub Releases](https://github.com/appledragon/everythingByMdfind/releases).

## Contribuir

¡Las contribuciones son bienvenidas! No dude en enviar pull requests o abrir issues para correcciones de errores, solicitudes de funciones o mejoras generales.

## Licencia

Este proyecto está licenciado bajo la Licencia Apache 2.0 - consulte el archivo [LICENSE.md](LICENSE.md) para obtener más detalles.

## Autor

Apple Dragon

## Versión

1.3.7

## Agradecimientos

*   Gracias al equipo de PyQt6 por proporcionar un framework GUI potente y versátil.
*   Inspiración de otras excelentes herramientas de búsqueda de archivos.
