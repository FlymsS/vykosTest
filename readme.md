# Contexto 

## Sistema operativo
ubuntu 20.04

# Solución 
## Ejecución de todo el proceso
Todo el proceso se ejecuta dentro del script ``` process.sh```, por lo que se debe cambiar su modo con ``` chmod -x process.sh```, dando así permiso de ejecución. 

Dependiendo de si el proceso se llamara de forma manual basta con ejecutar ``` $path/process.sh  ```. Si se debe ejecutar cada que el servidor sea prendido se debe ejecutar: 
``` 
crontab -e
@reboot  /bin/bash $path/process.sh
```
Por otro lado si lo que se busca es ejecutarlo a cierta hora debemos escribir 
```
crontab -e 
*     *     *     *     *  $path/process.sh
-     -     -     -     -
|     |     |     |     |
|     |     |     |     +----- día de la semana (0 - 6) (Domingo=0)
|     |     |     +------- mes (1 - 12)
|     |     +--------- día del mes (1 - 31)
|     +----------- hora (0 - 23)
+------------- minuto (0 - 59)

```
Por ejemplo 
```
* 1 * * * $path/process.sh
```
Ejecutara el proceso todos los días a la 1 am.

### Proceso.sh
Entre la linea 1 y 6 se realiza la conexión, se descargas los archivos para guardarlos en la carpeta uncleanedFiles dentro del workspace. 

La linea 7 ejecuta la limpieza.

Las lineas 9 y 10 comprimen los archivos y los guardan en la ruta home/etl/visitas/bckp/[$date].zip, donde date es la fecha del día donde se ejecuta la limpieza. 

### Cleaning.py

En todas las clases he tratado de que los metodos tengan un nombre descriptivo, con el fin de que no sea necesario leer el código para entender su funcionamiento, ademas si algo sale mal es más sencillo dar con los errores. 

Este archivo ocupa 4 clases:
- StatistisClass: Esta clase se encarga de guardar las estadisticas en la base de datos. Se agrega class al final, porque statistcs es una palabra reservada.
- Error: Encargada de guardar los registros con error, su estructura es igual a statisticsClass, pero tiene una columna extra donde se guarda la razón por la que cada registro esta en esa tabla. 
- Visitas: Esta clase se encarga de guardar la información de las visitas
- Cleaning: Aquí se ocupan las 3 clases anteriores. No tiene contacto directo con la clase dbConection, cada clase se encarga de gestionar sus propios controles para almacenar la información. 

