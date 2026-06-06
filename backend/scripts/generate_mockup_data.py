"""
Genera data sintética para el Sistema Neovate.

Uso:
    cd backend
    .venv\\Scripts\\python.exe -m backend.scripts.generate_mockup_data

NO migra data real — sólo crea registros realistas para probar API y UI.
Idempotente: si ya existe data, hace un TRUNCATE previo (con confirmación CLI).

Genera: 100 empresas × 4 meses (Feb–May 2026)
        Distribución SS: 60% Cumple, 25% En mora, 15% Pendiente
"""

from __future__ import annotations

import random
import sys
from datetime import date, datetime, timedelta

from sqlalchemy import text

from backend.core.database import SessionLocal, engine
from backend.core.security import hash_password
from backend.models import (
    Colaborador,
    CoberturaFlag,
    EmpresaAliada,
    EstadoReporte,
    EstadoSeguimiento,
    PeriodoBaseSSFF,
    ReporteNomina,
    ReporteRechazo,
    ReporteSS,
    RolUsuario,
    SeguimientoMensual,
    Usuario,
)


# ─────────────────────────────────────────────────────────────────────────────
# Catálogos
# ─────────────────────────────────────────────────────────────────────────────

# 4 meses históricos: Feb–May 2026
PERIODOS = [(2026, 2), (2026, 3), (2026, 4), (2026, 5)]

SECTORES = [
    "Soluciones", "Servicios", "Logística", "Tecnología", "Comercializadora",
    "Distribuidora", "Consultora", "Inversiones", "Grupo", "Corporación",
    "Industrias", "Construcciones", "Importadora", "Exportadora", "Alianza",
]
CIUDADES = [
    "Bogotá", "Medellín", "Cali", "Barranquilla", "Bucaramanga",
    "Cartagena", "Manizales", "Pereira", "Cúcuta", "Ibagué",
]
TIPO_EMPRESA = ["S.A.S.", "Ltda.", "S.A.", "E.U.", "S.C.A."]

NOMBRES = [
    "Carlos", "Andrea", "Luis", "María", "Juan", "Sofía", "Andrés", "Laura",
    "Diego", "Camila", "Felipe", "Valentina", "Sergio", "Daniela", "Mateo",
    "Isabella", "Santiago", "Paula", "Nicolás", "Catalina", "Esteban", "Lucía",
]
APELLIDOS = [
    "Gómez", "Rodríguez", "Martínez", "López", "García", "Pérez", "Sánchez",
    "Ramírez", "Torres", "Flores", "Ruiz", "Hernández", "Jiménez", "Álvarez",
    "Moreno", "Vargas", "Castro", "Romero", "Suárez", "Mendoza", "Ortiz",
]
CARGOS = [
    "Asesor Comercial", "Analista de Datos", "Supervisor", "Coordinador",
    "Auxiliar Administrativo", "Desarrollador", "Contador", "Gerente Operativo",
    "Especialista TI", "Líder de Proyecto",
]
OPERADORES = [
    "APORTES EN LINEA", "ASOPAGOS", "COMPENSAR MI PLANILLA",
    "ENLACE", "SOI", "SIMPLE",
]
TIPOS_PLANILLA_SS = ["Resumen", "Individual", "Consolidada", "Pagada"]
TIPOS_PLANILLA_NOMINA = ["Reporte Nómina Mensual"]

MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}

# Distribución de estados: 60% Cumple, 25% En mora, 15% Pendiente
DIST_ESTADO = [
    (EstadoSeguimiento.CUMPLE,   60),
    (EstadoSeguimiento.EN_MORA,  25),
    (EstadoSeguimiento.PENDIENTE, 15),
]


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def generar_nit_unico(idx: int) -> tuple[str, str]:
    """Genera NIT y NIT9 únicos a partir de un índice."""
    base = 800_000_000 + idx * 1_111
    dv = (base % 7) + 1  # dígito verificador simulado
    nit9 = str(base)[:9]
    nit = f"{nit9}-{dv}"
    return nit, nit9


def generar_nombre_empresa(idx: int, rng: random.Random) -> str:
    sector = rng.choice(SECTORES)
    ciudad = rng.choice(CIUDADES)
    tipo = rng.choice(TIPO_EMPRESA)
    return f"{sector} {ciudad} {idx} {tipo}"


def elegir_estado(rng: random.Random) -> EstadoSeguimiento:
    estados = [e for e, _ in DIST_ESTADO]
    pesos = [p for _, p in DIST_ESTADO]
    return rng.choices(estados, weights=pesos)[0]


# ─────────────────────────────────────────────────────────────────────────────
# Limpieza
# ─────────────────────────────────────────────────────────────────────────────

def truncate_all(db) -> None:
    """Vacía todas las tablas, reiniciando IDs autoincrement."""
    tablas = [
        "push_subscription", "colaborador", "reporte_rechazo",
        "reporte_ss", "reporte_nomina", "seguimiento_mensual",
        "periodo_base_ssff", "empresa_aliada", "usuario",
    ]
    db.execute(text(f"TRUNCATE {', '.join(tablas)} RESTART IDENTITY CASCADE"))
    db.commit()


# ─────────────────────────────────────────────────────────────────────────────
# Generadores
# ─────────────────────────────────────────────────────────────────────────────

def crear_usuarios(db, empresas: list[EmpresaAliada]) -> None:
    """Crea usuarios de todos los roles — incluye analista y empresa."""
    empresa_demo = empresas[0]

    db.add_all([
        Usuario(
            username="admin",
            nombre="Administrador Neovate",
            email="admin@neovate.local",
            password_hash=hash_password("admin123"),
            rol=RolUsuario.ADMIN,
            activo=True,
            primer_login=False,
        ),
        Usuario(
            username="analista1",
            nombre="Analista Principal",
            email="analista@neovate.local",
            password_hash=hash_password("analista123"),
            rol=RolUsuario.ANALISTA,
            activo=True,
            primer_login=False,
        ),
        Usuario(
            username="empresa_demo",
            nombre=f"Portal {empresa_demo.nombre_empresa[:30]}",
            email="empresa@neovate.local",
            password_hash=hash_password("empresa123"),
            rol=RolUsuario.EMPRESA,
            nit_empresa=empresa_demo.nit9,
            activo=True,
            primer_login=False,
        ),
        Usuario(
            username="viewer",
            nombre="Consultor Neovate",
            email="viewer@neovate.local",
            password_hash=hash_password("viewer123"),
            rol=RolUsuario.VIEWER,
            activo=True,
            primer_login=True,
        ),
    ])
    db.flush()


def crear_empresas(db, rng: random.Random, n: int = 100) -> list[EmpresaAliada]:
    """Crea n empresas con NITs únicos."""
    empresas = []
    for i in range(n):
        nit, nit9 = generar_nit_unico(i)
        nombre = generar_nombre_empresa(i + 1, rng)
        e = EmpresaAliada(
            nit=nit,
            nit9=nit9,
            nombre_empresa=nombre,
            primer_mes=2, primer_anio=2026,
            ultimo_mes=5, ultimo_anio=2026,
            activa=True,
        )
        empresas.append(e)
        db.add(e)
    db.flush()
    return empresas


def crear_periodos_ssff(db, empresas: list[EmpresaAliada]) -> None:
    for anio, mes in PERIODOS:
        db.add(PeriodoBaseSSFF(
            anio=anio, mes=mes,
            mes_nombre=MESES_ES[mes],
            archivo=f"Base activos {MESES_ES[mes]} {anio}.xlsx",
            ruta=f"Bases SSFF/{anio}/Base activos {MESES_ES[mes]} {anio}.xlsx",
            fecha_proceso=datetime(anio, mes, 28, 9, 30),
            empresas_encontradas=len(empresas),
        ))
    db.flush()


def crear_colaboradores(db, empresas: list[EmpresaAliada], rng: random.Random) -> None:
    """10 colaboradores por empresa × 4 períodos."""
    for empresa in empresas:
        cedulas = [str(1_000_000_000 + rng.randint(0, 999_999_999)) for _ in range(10)]
        for anio, mes in PERIODOS:
            for cedula in cedulas:
                existe_pl = rng.choices([CoberturaFlag.SI, CoberturaFlag.NO], weights=[85, 15])[0]
                db.add(Colaborador(
                    cedula=cedula,
                    nombres=rng.choice(NOMBRES),
                    apellidos=f"{rng.choice(APELLIDOS)} {rng.choice(APELLIDOS)}",
                    nit_empresa=empresa.nit9,
                    nombre_empresa_legible=empresa.nombre_empresa,
                    cargo=rng.choice(CARGOS),
                    anio=anio, mes=mes,
                    existe_planilla=existe_pl,
                    novedad_retiro=(
                        rng.choices([CoberturaFlag.SI, CoberturaFlag.NO], weights=[10, 90])[0]
                        if existe_pl == CoberturaFlag.SI else CoberturaFlag.NA
                    ),
                    existe_nomina=rng.choices([CoberturaFlag.SI, CoberturaFlag.NO], weights=[80, 20])[0],
                ))
    db.flush()


def crear_reportes(db, empresas: list[EmpresaAliada], rng: random.Random) -> None:
    """ReporteSS y ReporteNomina con distribución 60/25/15."""
    rid = 1
    for anio, mes in PERIODOS:
        for empresa in empresas:
            # Mapeamos estado seguimiento → estado reporte
            est_seg = elegir_estado(rng)
            if est_seg == EstadoSeguimiento.CUMPLE:
                estado_rep = rng.choices(
                    [EstadoReporte.VALIDADO_OK, EstadoReporte.VALIDADO_INDIVIDUAL],
                    weights=[85, 15],
                )[0]
            elif est_seg == EstadoSeguimiento.EN_MORA:
                estado_rep = EstadoReporte.RECHAZADO
            else:
                estado_rep = None  # pendiente: sin reporte aún

            if estado_rep is not None:
                fpago = (
                    date(anio, mes, rng.randint(5, 28))
                    if estado_rep != EstadoReporte.RECHAZADO else None
                )
                db.add(ReporteSS(
                    id=f"SS-{anio}{mes:02d}-{rid:05d}",
                    nit=empresa.nit, nit9=empresa.nit9,
                    anio=anio, mes_obligacion=mes,
                    operador=rng.choice(OPERADORES),
                    aliado=empresa.nombre_empresa,
                    quien_envia=f"pagos@empresa{rid}.co",
                    tipo_planilla=rng.choice(TIPOS_PLANILLA_SS),
                    estado=estado_rep,
                    fecha_pago=fpago,
                    fecha_recepcion=datetime(anio, mes, rng.randint(1, 27), 10, 0),
                    cantidad_validos=rng.randint(5, 50) if estado_rep != EstadoReporte.RECHAZADO else 0,
                    rechazo=(
                        rng.choice([
                            "NIT no coincide con el del archivo",
                            "Mes/año del reporte no coincide",
                            "Tipo de planilla no soportado",
                            "Período fuera del plazo permitido",
                        ]) if estado_rep == EstadoReporte.RECHAZADO else None
                    ),
                ))
                rid += 1

            # ~55% de empresas envían nómina
            if rng.random() < 0.55 and estado_rep is not None:
                est_nom = rng.choices(
                    [EstadoReporte.VALIDADO_OK, EstadoReporte.RECHAZADO],
                    weights=[80, 20],
                )[0]
                db.add(ReporteNomina(
                    id=f"NOM-{anio}{mes:02d}-{rid:05d}",
                    nit=empresa.nit, nit9=empresa.nit9,
                    aliado=empresa.nombre_empresa,
                    anio=anio, mes_obligacion=mes,
                    estado=est_nom,
                    fecha_pago=date(anio, mes, rng.randint(5, 28)) if est_nom == EstadoReporte.VALIDADO_OK else None,
                    tipo_planilla=TIPOS_PLANILLA_NOMINA[0],
                    cantidad_validos=rng.randint(5, 50) if est_nom == EstadoReporte.VALIDADO_OK else 0,
                    rechazo="Formato no corresponde" if est_nom == EstadoReporte.RECHAZADO else None,
                ))
                rid += 1
    db.flush()


def crear_seguimientos(db, empresas: list[EmpresaAliada], rng: random.Random) -> None:
    """SeguimientoMensual por empresa × período con distribución 60/25/15."""
    hoy = date.today()
    for anio, mes in PERIODOS:
        plazo_ss = date(anio, mes, 15)
        plazo_nom = date(anio, mes, 5)

        for empresa in empresas:
            estado = elegir_estado(rng)

            if estado == EstadoSeguimiento.CUMPLE:
                fpago = plazo_ss - timedelta(days=rng.randint(0, 8))
                dias_mora = 0
            elif estado == EstadoSeguimiento.EN_MORA:
                fpago = plazo_ss + timedelta(days=rng.randint(1, 20))
                dias_mora = (fpago - plazo_ss).days
            else:
                fpago = None
                dias_mora = None

            db.add(SeguimientoMensual(
                nit9=empresa.nit9,
                anio=anio, mes=mes,
                mes_nombre=MESES_ES[mes],
                nombre_empresa=empresa.nombre_empresa,
                ss_fecha_plazo=plazo_ss,
                ss_fecha_pago=fpago,
                ss_estado=estado,
                ss_dias_mora=dias_mora,
                ss_fecha_verif=hoy if estado != EstadoSeguimiento.PENDIENTE else None,
                nomina_fecha_plazo=plazo_nom,
                nomina_fecha_pago=fpago,
                nomina_estado=estado,
                nomina_dias_mora=dias_mora,
                nomina_fecha_verif=hoy if estado != EstadoSeguimiento.PENDIENTE else None,
            ))
    db.flush()


def crear_rechazos(db, empresas: list[EmpresaAliada], rng: random.Random) -> None:
    motivos = [
        "Buzón de destinatario lleno",
        "Dirección de correo no existe",
        "Servidor SMTP rechazó el envío",
        "Spam: bloqueado por filtro de seguridad",
        "Timeout en la entrega",
    ]
    for i in range(10):
        empresa = rng.choice(empresas)
        anio, mes = rng.choice(PERIODOS)
        db.add(ReporteRechazo(
            nit=empresa.nit, nit9=empresa.nit9,
            aliado=empresa.nombre_empresa,
            anio=anio, mes=mes,
            fecha_rechazo=datetime(anio, mes, rng.randint(1, 28), 14, 0),
            destinatario=f"pagos@empresa{i}.co",
            asunto=f"Alerta de vencimiento SS {MESES_ES[mes]} {anio}",
            motivo=rng.choice(motivos),
            intento=rng.randint(1, 3),
        ))
    db.flush()


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main(skip_confirm: bool = False) -> None:
    print("\n[Neovate] Generando data de prueba — 100 empresas × 4 meses (Feb–May 2026)")
    print(f"   DB: {engine.url}\n")

    if not skip_confirm and "--yes" not in sys.argv:
        ans = input("[!] Esto BORRARA los datos actuales. Continuar? [s/N]: ").strip().lower()
        if ans not in ("s", "si", "sí", "y", "yes"):
            print("Cancelado.")
            return

    rng = random.Random(42)  # semilla fija para reproducibilidad

    with SessionLocal() as db:
        print("  - Truncando tablas...")
        truncate_all(db)

        print("  - Creando 100 empresas aliadas...")
        empresas = crear_empresas(db, rng, n=100)

        print("  - Creando usuarios (admin / analista / empresa / viewer)...")
        crear_usuarios(db, empresas)

        print(f"  - Creando periodos SSFF ({len(PERIODOS)} meses)...")
        crear_periodos_ssff(db, empresas)

        print("  - Creando colaboradores (10 × 100 empresas × 4 meses)...")
        crear_colaboradores(db, empresas, rng)

        print("  - Creando reportes SS y Nómina...")
        crear_reportes(db, empresas, rng)

        print("  - Creando seguimientos mensuales (100 empresas × 4 meses)...")
        crear_seguimientos(db, empresas, rng)

        print("  - Creando rechazos de correo de muestra...")
        crear_rechazos(db, empresas, rng)

        db.commit()

    print("\n[OK] Mockup data generada correctamente.")
    print(f"\n   Empresas: 100  |  Períodos: {len(PERIODOS)} (Feb–May 2026)")
    print("   Distribución SS: ~60% Cumple, ~25% En mora, ~15% Pendiente\n")
    print("Credenciales de acceso:")
    print("   admin       / admin123    (rol: admin)")
    print("   analista1   / analista123 (rol: analista)")
    print("   empresa_demo/ empresa123  (rol: empresa, nit vinculado)")
    print("   viewer      / viewer123   (rol: viewer, primer_login=True)\n")


if __name__ == "__main__":
    main(skip_confirm="--yes" in sys.argv)
