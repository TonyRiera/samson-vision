"""
📖 Versículos — Marcas espirituales decorativas de Samson Vision.

No alteran el trabajo. Son como animaciones o branding interno:
un recordatorio de que Sansón no "vio" con sus ojos,
su visión era el plan de Dios para destruir a los filisteos.
(Jueces 16:28-30)

Se imprimen a stderr con formato decorativo sin contaminar la salida.
"""

import random
import sys

BORDE = "━"
ANCHO = 58

VERSICULOS_ALABANZA = [
    ("Salmo 150:6", "Todo lo que respira alabe a Jehová. Aleluya."),
    ("Salmo 103:1", "Bendice, alma mía, a Jehová, y bendiga todo mi ser su santo nombre."),
    ("Apocalipsis 4:11", "Digno eres, Señor, de recibir gloria y honra y poder; porque tú creaste todas las cosas."),
    ("Salmo 95:6", "Venid, adoremos y postrémonos; arrodillémonos delante de Jehová nuestro Hacedor."),
    ("Salmo 100:4", "Entrad por sus puertas con acción de gracias, por sus atrios con alabanza."),
    ("Isaías 6:3", "Santo, santo, santo, Jehová de los ejércitos; toda la tierra está llena de su gloria."),
    ("Salmo 34:1", "Bendeciré a Jehová en todo tiempo; su alabanza estará de continuo en mi boca."),
    ("Salmo 150:2", "Alabadle por sus grandes proezas; alabadle conforme a la muchedumbre de su grandeza."),
    ("Salmo 148:13", "Alaben el nombre de Jehová, porque solo su nombre es enaltecido; su gloria es sobre tierra y cielos."),
    ("1 Crónicas 16:34", "Alabad a Jehová, porque él es bueno; porque su misericordia es eterna."),
    ("Salmos 136:1", "Alabad a Jehová, porque él es bueno; porque para siempre es su misericordia."),
    ("Hebreos 13:15", "Así que, ofrezcamos siempre a Dios sacrificio de alabanza, es decir, fruto de labios que confiesan su nombre."),
]

VERSICULOS_SANSON = [
    ("Jueces 13:5", "Porque el niño será nazareo a Dios desde su nacimiento, y él comenzará a salvar a Israel de mano de los filisteos."),
    ("Jueces 14:6", "Y el Espíritu de Jehová vino sobre Sansón, y despedazó al león como quien despedaza un cabrito, sin tener nada en su mano."),
    ("Jueces 15:14", "Y el Espíritu de Jehová vino sobre él, y las cuerdas que estaban en sus brazos se volvieron como lino quemado con fuego."),
    ("Jueces 16:28", "Entonces clamó Sansón a Jehová, y dijo: Señor Jehová, acuérdate ahora de mí, y fortaléceme, te ruego, solamente esta vez, oh Dios."),
    ("Jueces 16:30", "Y los muertos que mató al morir fueron más que los que había matado durante su vida."),
]

TODOS = VERSICULOS_ALABANZA + VERSICULOS_SANSON


def _caja(ref: str, texto: str) -> str:
    """Dibuja una caja decorativa alrededor del versículo."""
    lineas = []
    lineas.append(f"  ┏{BORDE * ANCHO}┓")
    lineas.append(f"  ┃  📖 {ref:<{ANCHO - 6}}┃")
    lineas.append(f"  ┃  {BORDE * (ANCHO - 4)}  ┃")
    # Envolver texto si es muy largo
    palabras = texto.split()
    linea_actual = ""
    for palabra in palabras:
        if len(linea_actual) + len(palabra) + 1 > ANCHO - 6:
            lineas.append(f"  ┃  {linea_actual:<{ANCHO - 4}}┃")
            linea_actual = palabra
        else:
            linea_actual = f"{linea_actual} {palabra}".strip()
    if linea_actual:
        lineas.append(f"  ┃  {linea_actual:<{ANCHO - 4}}┃")
    lineas.append(f"  ┗{BORDE * ANCHO}┛")
    return "\n".join(lineas)


def imprimir(stream=sys.stderr):
    """Imprime un versículo aleatorio con formato decorativo."""
    ref, texto = random.choice(TODOS)
    print("", file=stream)
    print(_caja(ref, texto), file=stream)
    print("", file=stream)
    return ref, texto


def imprimir_alabanza(stream=sys.stderr):
    """Imprime un versículo de alabanza aleatorio con formato decorativo."""
    ref, texto = random.choice(VERSICULOS_ALABANZA)
    print("", file=stream)
    print(_caja(ref, texto), file=stream)
    print("", file=stream)
    return ref, texto


def imprimir_sanson(stream=sys.stderr):
    """Imprime un versículo de Sansón aleatorio con formato decorativo."""
    ref, texto = random.choice(VERSICULOS_SANSON)
    print("", file=stream)
    print(_caja(ref, texto), file=stream)
    print("", file=stream)
    return ref, texto


if __name__ == "__main__":
    imprimir()
