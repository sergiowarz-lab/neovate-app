"""
Modelos SQLAlchemy del Sistema Neovate.

Mapeo derivado de docs/DIAGRAMA_BASE_DATOS.md del sistema legacy.
La unión transversal entre entidades es NIT9 (primeros 9 dígitos del NIT).
"""

from datetime import date, datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean,
    CHAR,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    PrimaryKeyConstraint,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base


# ─────────────────────────────────────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────────────────────────────────────


class EstadoReporte(str, PyEnum):
    VALIDADO_OK = "Validado_ok"
    RECHAZADO = "Rechazado"
    VALIDADO_INDIVIDUAL = "Validado_individual"


class EstadoSeguimiento(str, PyEnum):
    CUMPLE = "Cumple"
    EN_MORA = "En_mora"
    PENDIENTE = "Pendiente"


class CoberturaFlag(str, PyEnum):
    SI = "SI"
    NO = "NO"
    NA = "N/A"


class RolUsuario(str, PyEnum):
    ADMIN = "admin"
    VIEWER = "viewer"


# ─────────────────────────────────────────────────────────────────────────────
# Empresa Aliada (raíz del modelo, unida por NIT9)
# ─────────────────────────────────────────────────────────────────────────────


class EmpresaAliada(Base):
    __tablename__ = "empresa_aliada"

    nit: Mapped[str] = mapped_column(String(15), primary_key=True)
    nit9: Mapped[str] = mapped_column(CHAR(9), unique=True, index=True, nullable=False)
    nombre_empresa: Mapped[str] = mapped_column(String(200), nullable=False)
    primer_mes: Mapped[int | None] = mapped_column(Integer)
    primer_anio: Mapped[int | None] = mapped_column(Integer)
    ultimo_mes: Mapped[int | None] = mapped_column(Integer)
    ultimo_anio: Mapped[int | None] = mapped_column(Integer)
    activa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    reportes_ss: Mapped[list["ReporteSS"]] = relationship(
        back_populates="empresa", cascade="all, delete-orphan"
    )
    reportes_nomina: Mapped[list["ReporteNomina"]] = relationship(
        back_populates="empresa", cascade="all, delete-orphan"
    )
    seguimientos: Mapped[list["SeguimientoMensual"]] = relationship(
        back_populates="empresa", cascade="all, delete-orphan"
    )
    colaboradores: Mapped[list["Colaborador"]] = relationship(
        back_populates="empresa", cascade="all, delete-orphan"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Reportes (planillas validadas)
# ─────────────────────────────────────────────────────────────────────────────


class ReporteSS(Base):
    __tablename__ = "reporte_ss"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    nit: Mapped[str] = mapped_column(String(15), nullable=False)
    nit9: Mapped[str] = mapped_column(
        CHAR(9), ForeignKey("empresa_aliada.nit9"), index=True, nullable=False
    )
    anio: Mapped[int] = mapped_column(Integer, nullable=False)
    mes_obligacion: Mapped[int] = mapped_column(Integer, nullable=False)
    operador: Mapped[str | None] = mapped_column(String(100))
    aliado: Mapped[str | None] = mapped_column(String(200))
    quien_envia: Mapped[str | None] = mapped_column(String(200))
    tipo_planilla: Mapped[str | None] = mapped_column(String(100))
    estado: Mapped[EstadoReporte] = mapped_column(
        Enum(EstadoReporte, name="estado_reporte"), nullable=False
    )
    fecha_pago: Mapped[date | None] = mapped_column(Date)
    fecha_recepcion: Mapped[datetime | None] = mapped_column(DateTime)
    cantidad_validos: Mapped[int | None] = mapped_column(Integer)
    rechazo: Mapped[str | None] = mapped_column(Text)

    empresa: Mapped["EmpresaAliada"] = relationship(back_populates="reportes_ss")


class ReporteNomina(Base):
    __tablename__ = "reporte_nomina"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    nit: Mapped[str] = mapped_column(String(15), nullable=False)
    nit9: Mapped[str] = mapped_column(
        CHAR(9), ForeignKey("empresa_aliada.nit9"), index=True, nullable=False
    )
    aliado: Mapped[str | None] = mapped_column(String(200))
    anio: Mapped[int] = mapped_column(Integer, nullable=False)
    mes_obligacion: Mapped[int] = mapped_column(Integer, nullable=False)
    estado: Mapped[EstadoReporte] = mapped_column(
        Enum(EstadoReporte, name="estado_reporte"), nullable=False
    )
    fecha_pago: Mapped[date | None] = mapped_column(Date)
    tipo_planilla: Mapped[str | None] = mapped_column(String(100))
    cantidad_validos: Mapped[int | None] = mapped_column(Integer)
    rechazo: Mapped[str | None] = mapped_column(Text)

    empresa: Mapped["EmpresaAliada"] = relationship(back_populates="reportes_nomina")


class ReporteRechazo(Base):
    """Hoja 'Rechazos' de BaseSeguimiento.xlsx — correos / envíos rechazados."""

    __tablename__ = "reporte_rechazo"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nit: Mapped[str | None] = mapped_column(String(15))
    nit9: Mapped[str | None] = mapped_column(CHAR(9), index=True)
    aliado: Mapped[str | None] = mapped_column(String(200))
    anio: Mapped[int | None] = mapped_column(Integer)
    mes: Mapped[int | None] = mapped_column(Integer)
    fecha_rechazo: Mapped[datetime | None] = mapped_column(DateTime)
    destinatario: Mapped[str | None] = mapped_column(String(200))
    asunto: Mapped[str | None] = mapped_column(String(255))
    motivo: Mapped[str | None] = mapped_column(Text)
    intento: Mapped[int | None] = mapped_column(Integer, default=1)


# ─────────────────────────────────────────────────────────────────────────────
# Seguimiento mensual (estado SS + Nómina por empresa × período)
# ─────────────────────────────────────────────────────────────────────────────


class SeguimientoMensual(Base):
    __tablename__ = "seguimiento_mensual"
    __table_args__ = (
        PrimaryKeyConstraint("nit9", "anio", "mes", name="pk_seguimiento_mensual"),
    )

    nit9: Mapped[str] = mapped_column(
        CHAR(9), ForeignKey("empresa_aliada.nit9"), nullable=False
    )
    anio: Mapped[int] = mapped_column(Integer, nullable=False)
    mes: Mapped[int] = mapped_column(Integer, nullable=False)
    mes_nombre: Mapped[str | None] = mapped_column(String(20))
    nombre_empresa: Mapped[str | None] = mapped_column(String(200))

    ss_fecha_plazo: Mapped[date | None] = mapped_column(Date)
    ss_fecha_pago: Mapped[date | None] = mapped_column(Date)
    ss_estado: Mapped[EstadoSeguimiento | None] = mapped_column(
        Enum(EstadoSeguimiento, name="estado_seguimiento")
    )
    ss_dias_mora: Mapped[int | None] = mapped_column(Integer)
    ss_fecha_verif: Mapped[date | None] = mapped_column(Date)

    nomina_estado: Mapped[EstadoSeguimiento | None] = mapped_column(
        Enum(EstadoSeguimiento, name="estado_seguimiento")
    )
    nomina_fecha_plazo: Mapped[date | None] = mapped_column(Date)
    nomina_fecha_pago: Mapped[date | None] = mapped_column(Date)
    nomina_dias_mora: Mapped[int | None] = mapped_column(Integer)
    nomina_fecha_verif: Mapped[date | None] = mapped_column(Date)

    empresa: Mapped["EmpresaAliada"] = relationship(back_populates="seguimientos")


# ─────────────────────────────────────────────────────────────────────────────
# Bases SSFF (período = año+mes)
# ─────────────────────────────────────────────────────────────────────────────


class PeriodoBaseSSFF(Base):
    __tablename__ = "periodo_base_ssff"
    __table_args__ = (
        PrimaryKeyConstraint("anio", "mes", name="pk_periodo_base_ssff"),
    )

    anio: Mapped[int] = mapped_column(Integer, nullable=False)
    mes: Mapped[int] = mapped_column(Integer, nullable=False)
    mes_nombre: Mapped[str | None] = mapped_column(String(20))
    archivo: Mapped[str | None] = mapped_column(String(255))
    ruta: Mapped[str | None] = mapped_column(String(500))
    fecha_proceso: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())
    empresas_encontradas: Mapped[int | None] = mapped_column(Integer, default=0)


class Colaborador(Base):
    __tablename__ = "colaborador"
    __table_args__ = (
        UniqueConstraint("cedula", "anio", "mes", name="uq_colaborador_periodo"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cedula: Mapped[str] = mapped_column(String(15), index=True, nullable=False)
    nombres: Mapped[str | None] = mapped_column(String(100))
    apellidos: Mapped[str | None] = mapped_column(String(100))
    nit_empresa: Mapped[str] = mapped_column(
        CHAR(9), ForeignKey("empresa_aliada.nit9"), index=True, nullable=False
    )
    cargo: Mapped[str | None] = mapped_column(String(100))
    empresa: Mapped["EmpresaAliada"] = relationship(back_populates="colaboradores")
    nombre_empresa_legible: Mapped[str | None] = mapped_column(String(200))

    anio: Mapped[int] = mapped_column(Integer, nullable=False)
    mes: Mapped[int] = mapped_column(Integer, nullable=False)

    existe_planilla: Mapped[CoberturaFlag | None] = mapped_column(
        Enum(CoberturaFlag, name="cobertura_flag")
    )
    novedad_retiro: Mapped[CoberturaFlag | None] = mapped_column(
        Enum(CoberturaFlag, name="cobertura_flag")
    )
    existe_nomina: Mapped[CoberturaFlag | None] = mapped_column(
        Enum(CoberturaFlag, name="cobertura_flag")
    )


# ─────────────────────────────────────────────────────────────────────────────
# Usuarios del portal
# ─────────────────────────────────────────────────────────────────────────────


class Usuario(Base):
    __tablename__ = "usuario"

    username: Mapped[str] = mapped_column(String(50), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str | None] = mapped_column(String(200))
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[RolUsuario] = mapped_column(
        Enum(RolUsuario, name="rol_usuario"), nullable=False, default=RolUsuario.VIEWER
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    primer_login: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    ultimo_acceso: Mapped[datetime | None] = mapped_column(DateTime)
