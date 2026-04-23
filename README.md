# ReVIP — Plataforma de Reservaciones con Trust Score

## Descripción
Sistema de reservaciones para establecimientos de alta gama. Implementa el **patrón de diseño Proxy** para validar el Trust Score del cliente antes de procesar una reserva.

## Casos de Uso Implementados
1. **Registrar Establecimiento** — Actor: Socio (Restaurante)
2. **Realizar Reservación** — Actor: Cliente (con Proxy de validación)

## Instrucciones de Ejecución

### 1. Instalar dependencias
```bash
pip install flask
```

### 2. Ejecutar la aplicación
```bash
python app.py
```

### 3. Abrir en el navegador
```
http://127.0.0.1:5000
```

## Clientes de Prueba (cargados automáticamente)
| ID   | Nombre          | Trust Score |
|------|-----------------|-------------|
| C001 | Ana García      | 85          |
| C002 | Luis Martínez   | 45          |
| C003 | Sofía Ruiz      | 95          |

## Flujo de Prueba
1. Ir a **Registrar Establecimiento** y crear uno con umbral 70
2. Ir a **Realizar Reservación** y probar con Luis (score 45) → el Proxy lo rechaza
3. Probar con Ana (score 85) → el Proxy lo aprueba y delega al ServicioReal

## Estructura del Proyecto
```
revip/
├── app.py                  
├── datos/
│   ├── clientes.json
│   ├── establecimientos.json
│   └── reservaciones.json
└── templates/
    ├── base.html
    ├── inicio.html
    ├── registrar_establecimiento.html
    ├── lista_establecimientos.html
    ├── reservar.html
    └── lista_reservaciones.html
```
