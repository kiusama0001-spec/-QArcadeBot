import os
import uvicorn
from webapp.app import app

if __name__ == "__main__":
    # Render asigna un puerto dinámico mediante la variable de entorno PORT.
    # Si no existe (por ejemplo, si lo pruebas en tu computadora), usará el puerto 8000 por defecto.
    port = int(os.environ.get("PORT", 8000))
    
    # Arranca la aplicación escuchando en todas las interfaces (0.0.0.0) y en el puerto correcto de Render
    uvicorn.run(app, host="0.0.0.0", port=port
               )
