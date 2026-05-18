"""
Genera data sintética para el Sistema Neovate.

Uso:
    cd backend
    .venv\\Scripts\\python.exe -m backend.scripts.generate_mockup_data

NO migra data real — sólo crea registros realistas para probar API y UI.
Idempotente: si ya existe data, hace un TRUNCATE previo (con confirmación CLI).
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

EMPRESAS = [
    ("900123456-1", "900123456", "Soluciones Empresariales Andinas S.A.S."),
    ("800987654-3", "800987654", "Logística del Caribe Ltda."),
    ("901234567-8", "901234567", "Tecnología y Servicios Bogotá S.A."),
    ("830014450-3", "830014450", "Comercializadora del Pacífico S.A.S."),
    ("860001234-5", "860001234", "Distribuidora Nacional Aliada Ltda."),
]

NOMBRES = [
    "Carlos", "Andrea", "Luis", "María", "Juan", "Sofía", "Andrés", "Laura",
    "Diego", "Camila", "Felipe", "Valentina", "Sergio", "Daniela", "Mateo",
    "Isabella", "Santiago", "Paula", "Nicolás", "Catalina", "Esteban", "Lucía",
    "Tomás", "Manuela", "Samuel", "Antonia", "Martín", "Salomé", "Emilio", "Ana",
]

APELLIDOS = [
    "Gómez", "Rodríguez", "Martínez", "López", "García", "Pérez", "Sánchez",
    "Ramírez", "Torres", "Flores", "Ruiz", "Hernández", "Jiménez", "Álvarez",
    "Moreno", "Vargas", "Castro", "Romero", "Suárez", "Mendoza", "Ortiz",
    "Silva", "Rojas", "Cardona", "Bermúdez", "Marín", "Cárdenas", "Quintero",
]

CARGOS = [
    "Asesor Comercial", "Analista de Datos", "Supervisor", "Coordinador",
    "Auxiliar Administrativo", "Desarrollador", "Contador", "Gerente Operativo",
    "Especialista TI", "Líder de Proyecto", "Auxiliar Logístico",
]

OPERADORES = [
    "APORTES EN LINEA", "ASOPAGOS", "COMPENSAR", "ENLACE OPERATIVO",
    "SOI", "SIMPLE",
]

TIPOS_PLANILLA_SS = ["Resumen", "Individual", "Consolidada", "Pagada"]
TIPOS_PLANILLA_NOMINA = ["Reporte Nómina Mensual"]

MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}

# Período de prueba: últimos 3 meses (Mar–May 2026)
PERIODOS = [(2026, 3), (2026, 4), (2026, 5)]


# ─────────────────────────────────────────────────────────────────────────────
# Limpieza
# ─────────────────────────────────────────────────────────────────────────────

def truncate_all(db) -> None:
    """Vacía todas las tablas, reiniciando IDs autoincrement."""
    tablas = [
        "colaborador", "reporte_rechazo", "reporte_ss", "reporte_nomina",
        "seguimiento_mensual", "periodo_base_ssff", "empresa_aliada", "usuario",
    ]
    db.execute(text(f"TRUNCATE {', '.join(tablas)} RESTART IDENTITY CASCADE"))
    db.commit()


# ─────────────────────────────────────────────────────────────────────────────
# Generadores
# ─────────────────────────────────────────────────────────────────────────────

def crear_usuarios(db) -> None:
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


def crear_empresas(db) -> list[EmpresaAliada]:
    empresas = []
    for nit, nit9, nombre in EMPRESAS:
        e = EmpresaAliada(
            nit=nit,
            nit9=nit9,
            nombre_empresa=nombre,
            primer_mes=1, primer_anio=2025,
            ultimo_mes=5, ultimo_anio=2026,
            activa=True,
        )
        empresas.append(e)
        db.add(e)
    db.flush()
    return empresas


def crear_periodos_ssff(db) -> None:
    for anio, mes in PERIODOS:
        db.add(PeriodoBaseSSFF(
            anio=anio, mes=mes,
            mes_nombre=MESES_ES[mes],
            archivo=f"Base activos {MESES_ES[mes]} {anio}.xlsx",
            ruta=f"Bases SSFF/{anio}/Base activos {MESES_ES[mes]} {anio}.xlsx",
            fecha_proceso=datetime(anio, mes, 28, 9, 30),
            empresas_encontradas=len(EMPRESAS),
        ))
    db.flush()


def crear_colaboradores(db, empresas: list[EmpresaAliada]) -> None:
    """50 colaboradores únicos × 3 períodos = 150 registros."""
    base_colabs = []
    for i in range(50):
        empresa = empresas[i % len(empresas)]
        cedula = str(1_000_000_000 + random.randint(0, 99_999_999))
        base_colabs.append({
            "cedula": cedula,
            "nombres": random.choice(NOMBRES),
            "apellidos": f"{random.choice(APELLIDOS)} {random.choice(APELLIDOS)}",
            "nit_empresa": empresa.nit9,
            "nombre_empresa_legible": empresa.nombre_empresa,
            "cargo": random.choice(CARGOS),
        })

    for anio, mes in PERIODOS:
        for c in base_colabs:
            existe_pl = random.choices(
                [CoberturaFlag.SI, CoberturaFlag.NO], weights=[85, 15]
            )[0]
            db.add(Colaborador(
                **c,
                anio=anio, mes=mes,
                existe_planilla=existe_pl,
                novedad_retiro=(
                    random.choices([CoberturaFlag.SI, CoberturaFlag.NO], weights=[10, 90])[0]
                    if existe_pl == CoberturaFlag.SI else CoberturaFlag.NA
                ),
                existe_nomina=random.choices(
                    [CoberturaFlag.SI, CoberturaFlag.NO], weights=[80, 20]
                )[0],
            ))
    db.flush()


def crear_reportes(db, empresas: list[EmpresaAliada]) -> None:
    """~20 ReporteSS y ~10 ReporteNomina con estados variados."""
    rid = 1
    for anio, mes in PERIODOS:
        for empresa in empresas:
            estado = random.choices(
                [EstadoReporte.VALIDADO_OK, EstadoReporte.RECHAZADO, EstadoReporte.VALIDADO_INDIVIDUAL],
                weights=[70, 15, 15],
            )[0]
            fpago = (
                date(anio, mes, random.randint(5, 28))
                if estado != EstadoReporte.RECHAZADO else None
            )
            db.add(ReporteSS(
                id=f"SS-{anio}{mes:02d}-{rid:04d}",
                nit=empresa.nit, nit9=empresa.nit9,
                anio=anio, mes_obligacion=mes,
                operador=random.choice(OPERADORES),
                aliado=empresa.nombre_empresa,
                quien_envia=f"contacto@{empresa.nombre_empresa.lower().split()[0]}.com",
                tipo_planilla=random.choice(TIPOS_PLANILLA_SS),
                estado=estado,
                fecha_pago=fpago,
                fecha_recepcion=datetime(anio, mes, random.randint(1, 27), 10, 0),
                cantidad_validos=random.randint(5, 30) if estado != EstadoReporte.RECHAZADO else 0,
                rechazo=(
                    random.choice([
                        "NIT no coincide con el del archivo",
                        "Mes/año del reporte no coincide",
                        "Tipo de planilla no soportado",
                    ]) if estado == EstadoReporte.RECHAZADO else None
                ),
            ))
            rid += 1

            # ~50% de las empresas también envían nómina cada mes
            if random.random() < 0.55:
                est_nom = random.choices(
                    [EstadoReporte.VALIDADO_OK, EstadoReporte.RECHAZADO],
                    weights=[80, 20],
                )[0]
                db.add(ReporteNomina(
                    id=f"NOM-{anio}{mes:02d}-{rid:04d}",
                    nit=empresa.nit, nit9=empresa.nit9,
                    aliado=empresa.nombre_empresa,
                    anio=anio, mes_obligacion=mes,
                    estado=est_nom,
                    fecha_pago=date(anio, mes, random.randint(5, 28)) if est_nom == EstadoReporte.VALIDADO_OK else None,
                    tipo_planilla=TIPOS_PLANILLA_NOMINA[0],
                    cantidad_validos=random.randint(5, 30) if est_nom == EstadoReporte.VALIDADO_OK else 0,
                    rechazo="Formato no corresponde" if est_nom == EstadoReporte.RECHAZADO else None,
                ))
                rid += 1
    db.flush()


def crear_seguimientos(db, empresas: list[EmpresaAliada]) -> None:
    """Una fila por empresa × período con estado Cumple/Mora/Pendiente."""
    hoy = date.today()
    for anio, mes in PERIODOS:
        for empresa in empresas:
            plazo = date(anio, mes, 15)
            es_periodo_actual = (anio, mes) == (hoy.year, hoy.month)

            if es_periodo_actual:
                # mes en curso: la mayoría pendiente
                estado = random.choices(
                    [EstadoSeguimiento.PENDIENTE, EstadoSeguimiento.CUMPLE, EstadoSeguimiento.EN_MORA],
                    weights=[55, 35, 10],
                )[0]
            else:
                estado = random.choices(
                    [EstadoSeguimiento.CUMPLE, EstadoSeguimiento.EN_MORA],
                    weights=[75, 25],
                )[0]

            if estado == EstadoSeguimiento.CUMPLE:
                fpago = plazo - timedelta(days=random.randint(0, 8))
                dias_mora = 0
            elif estado == EstadoSeguimiento.EN_MORA:
                fpago = plazo + timedelta(days=random.randint(1, 12))
                dias_mora = (fpago - plazo).days
            else:
                fpago = None
                dias_mora = None

            db.add(SeguimientoMensual(
                nit9=empresa.nit9,
                anio=anio, mes=mes,
                mes_nombre=MESES_ES[mes],
                nombre_empresa=empresa.nombre_empresa,
                ss_fecha_plazo=plazo,
                ss_fecha_pago=fpago,
                ss_estado=estado,
                ss_dias_mora=dias_mora,
                ss_fecha_verif=hoy if estado != EstadoSeguimiento.PENDIENTE else None,
                nomina_fecha_plazo=date(anio, mes, 5),
                nomina_fecha_pago=fpago,
                nomina_estado=estado,
                nomina_dias_mora=dias_mora,
                nomina_fecha_verif=hoy if estado != EstadoSeguimiento.PENDIENTE else None,
            ))
    db.flush()


def crear_rechazos(db, empresas: list[EmpresaAliada]) -> None:
    """5 envíos rechazados de muestra."""
    motivos = [
        "Buzón de destinatario lleno",
        "Dirección de correo no existe",
        "Servidor SMTP rechazó el envío",
        "Spam: bloqueado por filtro de seguridad",
        "Timeout en la entrega",
    ]
    for i in range(5):
        empresa = random.choice(empresas)
        anio, mes = random.choice(PERIODOS)
        db.add(ReporteRechazo(
            nit=empresa.nit, nit9=empresa.nit9,
            aliado=empresa.nombre_empresa,
            anio=anio, mes=mes,
            fecha_rechazo=datetime(anio, mes, random.randint(1, 28), 14, 0),
            destinatario=f"pagos@{empresa.nombre_empresa.lower().split()[0]}.com",
            asunto=f"Alerta de vencimiento SS {MESES_ES[mes]} {anio}",
            motivo=motivos[i],
            intento=random.randint(1, 3),
        ))
    db.flush()


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main(skip_confirm: bool = False) -> None:
    print("\n[Neovate] Generando data de prueba")
    print(f"   DB: {engine.url}\n")

    if not skip_confirm and "--yes" not in sys.argv:
        ans = input("[!] Esto BORRARA los datos actuales. Continuar? [s/N]: ").strip().lower()
        if ans not in ("s", "si", "sí", "y", "yes"):
            print("Cancelado.")
            return

    random.seed(42)  # reproducible

    with SessionLocal() as db:
        print("  - Truncando tablas...")
        truncate_all(db)

        print("  - Creando usuarios (admin / viewer)...")
        crear_usuarios(db)

        print("  - Creando 5 empresas aliadas...")
        empresas = crear_empresas(db)

        print(f"  - Creando periodos SSFF ({len(PERIODOS)} meses)...")
        crear_periodos_ssff(db)

        print("  - Creando 50 colaboradores x 3 periodos = 150 registros...")
        crear_colaboradores(db, empresas)

        print("  - Creando reportes SS y Nomina...")
        crear_reportes(db, empresas)

        print("  - Creando seguimientos mensuales...")
        crear_seguimientos(db, empresas)

        print("  - Creando 5 rechazos de correo...")
        crear_rechazos(db, empresas)

        db.commit()

    print("\n[OK] Mockup data generada correctamente.")
    print("\nCredenciales de acceso:")
    print("   admin  / admin123   (rol: admin)")
    print("   viewer / viewer123  (rol: viewer, primer_login=True)\n")


if __name__ == "__main__":
    main(skip_confirm="--yes" in sys.argv)
