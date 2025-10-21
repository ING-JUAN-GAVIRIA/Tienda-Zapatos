# Tienda de Zapatos — Sistema Web con Flask y PostgreSQL

##Descripción del Proyecto
La **Tienda de Zapatos** es una aplicación web desarrollada en **Flask** que permite gestionar productos (zapatos), incluyendo su registro, listado, búsqueda y carga de imágenes.  

## Dominio Elegido
**Comercio electrónico de calzado.**

**Justificación:**  
Se eligió este dominio por su aplicabilidad práctica: el manejo de inventarios, catálogos de productos y la posibilidad de expansión hacia ventas en línea son casos de uso muy comunes y útiles para negocios reales.

## Instrucciones de Instalación

### Clonar el repositorio
```bash
git clone https://github.com/ING-JUAN-GAVIRIA/Tienda-Zapatos.git
cd tienda_zapatos
```

### Crear entorno con Rye
Si no tienes **Rye** instalado, primero ejecuta:
```bash
pip install rye
```

Luego crea y activa el entorno:
```bash
rye init
rye sync
```

### Instalar dependencias
```bash
rye add flask psycopg2-binary sqlalchemy python-dotenv
```

## Configuración de la Base de Datos (PostgreSQL)

1. Abre **pgAdmin** o tu consola de PostgreSQL.
2. Crea una base de datos:
   ```sql
   CREATE DATABASE tienda_zapatos;
   ```
3. Crea un usuario (si aún no lo tienes):
   ```sql
   CREATE USER admin WITH PASSWORD 'admin123';
   ALTER ROLE admin SET client_encoding TO 'utf8';
   ALTER ROLE admin SET default_transaction_isolation TO 'read committed';
   ALTER ROLE admin SET timezone TO 'UTC';
   GRANT ALL PRIVILEGES ON DATABASE tienda_zapatos TO admin;
   ```

## Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:

```bash
FLASK_ENV=development
FLASK_APP=src/tienda_zapatos/app.py
SECRET_KEY=clave_super_segura
DATABASE_URL=postgresql://admin:juandiego@localhost:5432/tienda_bd
UPLOAD_FOLDER=src/tienda_zapatos/static/uploads
```

## Cómo Ejecutar la Aplicación

### Desde terminal:
```bash
flask run
```

O bien:
```bash
python run.py
```

Luego abre en tu navegador:
```
http://127.0.0.1:5000/
```

## Rutas Disponibles

| Método | Ruta | Descripción |
|--------|-------|-------------|
| GET | `/` | Página de inicio |
| GET | `/login` | Muestra el formulario de inicio de sesión |
| POST | `/login` | Procesa las credenciales del usuario |
| GET | `/productos` | Lista de productos registrados |
| GET | `/productos/nuevo` | Formulario para registrar un nuevo producto |
| POST | `/productos/crear` | Guarda un producto en la base de datos |
| GET | `/productos/<id>` | Muestra el detalle de un producto |
| POST | `/productos/buscar` | Permite buscar productos por nombre o categoría |
| GET | `/uploads/<filename>` | Sirve las imágenes almacenadas en `static/uploads` |

##  Características Implementadas

 Registro, modificación y eliminación de productos  
 Carga y visualización de imágenes de productos  
 Sistema de autenticación básica (login/logout)  
 Búsqueda por nombre o categoría  
 Panel administrativo con navegación coherente  
 Estilos unificados entre vistas (login, navbar, etc.)  
 Configuración centralizada de Flask y base de datos  
 Manejo de archivos subidos con límite de tamaño (4MB)

##  Modelos de Datos

### `Producto`
| Campo | Tipo | Descripción |
|--------|------|-------------|
| `id` | Integer | Identificador único |
| `nombre` | String | Nombre del zapato |
| `precio` | Float | Precio del producto |
| `categoria` | String | Categoría o tipo de calzado |
| `descripcion` | Text | Detalle del producto |
| `image_filename` | String | Nombre del archivo de imagen |
| `fecha_creacion` | DateTime | Fecha en que se registró el producto |

Relaciones:
- En futuras versiones, se incluirán tablas de **Usuarios** y **Pedidos** para manejar autenticación y compras.

```

## Tecnologías Usadas

- **Flask** — Framework web principal  
- **PostgreSQL** — Base de datos relacional  
- **SQLAlchemy** — ORM para manejar modelos y consultas  
- **HTML5, CSS3, Bootstrap** — Interfaz de usuario  
- **Python-dotenv** — Gestión de variables de entorno  
- **Werkzeug** — Manejo de archivos subidos  

## Próximas Mejoras

- Sistema de usuarios con roles (admin, vendedor)  
- Paginación de productos  
- Panel estadístico (ventas e inventario)  
- Integración con API de pagos  
- Implementación en la nube (Render / Railway / AWS)
