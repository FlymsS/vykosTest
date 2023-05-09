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

---

### .env.template
Este es un template para variable de enterno, por lo que necesita actualizarce antes de ejecutar process.sh por primera vez, ademas debe cambiarse su nombre por .env

Esta incluido dentro de .gitignore, por lo que esta configuración debe hacerse hasta que se clone el proyecto donde se va a ejecutar.

---

### Process.sh
Entre la linea 1 y 6 se realiza la conexión, se descargas los archivos para guardarlos en la carpeta uncleanedFiles dentro del workspace. 

La linea 7 ejecuta la limpieza.

Las lineas 9 y 10 comprimen los archivos y los guardan en la ruta home/etl/visitas/bckp/[$date].zip, donde date es la fecha del día donde se ejecuta la limpieza. 

---

### Cleaning.py

Para los procesos de lectura y limpieza ocupo pandas, esto permite trabajar de manera rápida, ademas de que su documentación y comunidad es extensa.

En todas las clases he tratado de que los metodos tengan un nombre descriptivo, con el fin de que no sea necesario leer el código para entender su funcionamiento, ademas si algo sale mal es más sencillo dar con los errores. 

Este archivo ocupa 4 clases:
- StatistisClass: Esta clase se encarga de guardar las estadisticas en la base de datos. Se agrega class al final, porque statistcs es una palabra reservada.
- Error: Encargada de guardar los registros con error, su estructura es igual a statisticsClass, pero tiene una columna extra donde se guarda la razón por la que cada registro esta en esa tabla. 
- Visitas: Esta clase se encarga de guardar la información de las visitas
- Cleaning: Aquí se ocupan las 3 clases anteriores. No tiene contacto directo con la clase dbConection, cada clase se encarga de gestionar sus propios controles para almacenar la información. 

Las variables globales **path** y **pathLog** estan escritas de ese modo por si desea modificarse las rutas donde se guardan los archivos al descargar los registros del servidor y donde se guardaran las bitacoras. Sin embargo se debe tener en cuenta que al modificarlos tambien se debe modificar la ruta dentro de process.sh. 

Dentro de cleaning todo ocurre en ```fileSelection()```, en esta función los archivos dentro de la carpeta uncleanedFiles son leídos y limpiados, si algo ocurre al tratar de guardar la información en la bd se agrega a la bitacora que hubo un error y se continua con el siguiente archivo.

La forma en la que cada archivo se limpieza es la siguiente: 

* Se verifica que el email indicado haga match con la variable global regexEmail, en caso de no cumplir esa fila se agrega al df.erroresEmail. 
* Se verifica que la fecha de Fecha_open tenga el formato indicado, en caso de contrario se agrega esa fila al df.invalidDateDF1. La info que salga de este resultado se ocupara para guardar en la tabla visitas.
* Se verifica que la fecha de Fecha_open tenga el formato indicado, en caso de contrario se agrega esa fila al df.invalidDateDF2.

En los 3 casos se ocupa una variable de entorno para guardar cuantas filas tiene cada df, esto se ocupa al finalizar el guardado en la bd para saber cuantos registros se procesaron.

El siguiente paso es guardar la información en la tabla visitas. Como dije antes solo se ocupa la que resulto correcta en el formato de email y el formato en Fecha_open, solo estos dos se ocupan para esta tabla.

El siguiente paso es guardar la tabla statistics y errores. 
Este guardado es casí directo, no hay que verificar actualizaciónes, en ambos casos lo que hay que hacer es verificar si la tabla contiene la columna jyv, jk o fgh. En la tabla solo se existe la columna jyv, por lo que se hace un cambio en el nombre la cabecera. Ademas se redondea la información para que sea un int y se hace un cast de str a int. 

En todos los casos se verifica que el df tenga filas, pues el metodo iterrows() de pandas no funciona si el df no tiene registros, los df de error son nulls hasta que hay un error. Si ningun archivo tiene, por ejemplo, la fecha en un formato incorrecto esto podria traer un error y evitar que se guarde la informacion correcta en la bd. 

---

### Errors y StatiticsClass

Ambas clases solamente reciben la información y la guardan en la bd. 

---

### Visits 

Cuando se recibe la información, la fecha de envio se cambia al formato "yyyy/mm/dd"

Antes de guardar un registro se hace una consulta a la base de datos, si el resultado no contiene columnas se realiza el registro y listo.

Por otro lado si el resultado si tiene filas se: 
 * Obtiene el total de visitas y se aumenta en uno. 
 * De la ultima fecha registrada se obtiene el año, si este es igual al de la fecha dada se aumenta en uno la cantidad de visitas del año actual y se pasa a verificar el mes. De caso contario la cantidad de visitas del año actual pasa a 1 al igual que la cantidad de visitas del mes actual.
 * (opcional) Se compara el mes de la ultima visita registrada con la del dado, en caso de ser el mismo se aumenta en 1, en caso contario el número de visitas del mes pasa a ser 1. 
 * Se verifica que la fecha de ultima visita sea posterior a la obtenida por la consulta, de no ser así la obtenida en la consulta se cambia por la dada.
 * Se verifica que la fecha de primera visita sea anterior a la de la dada, de ser así no se hace cambio, caso contrario, la primera visita tambien se actualiza.

Finalmente se gaurda en la base de datos

---
### dbConection

Para la conexión con la base de datos las 3 clases ocupan una instancia de esta dbConection. 

Esto permite tener en un solo lugar los cambios de la bd. Ocupo como ORM sqlAlchemy, esto permite manejar las tablas como clases (justo lo que hice) y evitar así que al agregar datos tenga que escribir la consulta como tal y permita mandar unicamente la calse para hacer un insert y un update. Estoy seguro que existen formas más eficientes de obtener la información de una consulta a como lo hice en visits: 

```
query = text(f"SELECT * FROM visitas WHERE email = '{self.email}'")
res = connection.execute(query)
```

Pero desconozco esta forma, sin embargo utilizar esta herramiento me fue de gran útilidad. 
