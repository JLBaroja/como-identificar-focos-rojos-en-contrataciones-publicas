#!/usr/bin/env python

# Created by Raul Peralta-Lozada (11/10/17)
import pandas as pd
from typing import List, Tuple

DataFrame = pd.DataFrame


def interaccion_rfc_fantasma(df_procs, df_rfc_fantasma, **kwargs):
    df_feature = pd.DataFrame(
        data=df_procs.CLAVEUC.unique(), columns=['CLAVEUC'])
    df = pd.merge(
        df_procs, df_rfc_fantasma, on='PROVEEDOR_CONTRATISTA', how='inner'
    )
    monto_por_contrato = df.groupby(
        ['DEPENDENCIA', 'CLAVEUC', 'PROVEEDOR_CONTRATISTA',
         'NUMERO_PROCEDIMIENTO', 'CODIGO_CONTRATO'],
        as_index=False).IMPORTE_PESOS.sum()
    # número de proveedores fantasma por uc
    pocs_distintos = monto_por_contrato.groupby(
        'CLAVEUC').PROVEEDOR_CONTRATISTA.nunique()
    pocs_distintos = pocs_distintos.reset_index()
    pocs_distintos = pocs_distintos.rename(
        columns={'PROVEEDOR_CONTRATISTA': 'num_proveedores_fantasma'})
    # número de contratos con rfc fantasmas por uc
    contratos_total = monto_por_contrato.groupby(
        ['CLAVEUC', 'NUMERO_PROCEDIMIENTO']).CODIGO_CONTRATO.nunique()
    contratos_total = contratos_total.reset_index()
    contratos_total = contratos_total.rename(
        columns={'CODIGO_CONTRATO': 'contratos_con_fantasmas'})
    contratos_total = contratos_total.groupby(
        'CLAVEUC', as_index=False).contratos_con_fantasmas.sum()
    # monto con rfc fantasmas por uc
    monto_uc_contratos = monto_por_contrato.groupby(
        ['CLAVEUC', 'NUMERO_PROCEDIMIENTO', 'CODIGO_CONTRATO'],
        as_index=False).IMPORTE_PESOS.sum()
    monto_uc_contratos = monto_uc_contratos.groupby('CLAVEUC',
        as_index=False).IMPORTE_PESOS.sum()
    monto_uc_contratos = monto_uc_contratos.rename(
        columns={'IMPORTE_PESOS': 'monto_fantasma'})
    # join the features
    df_feature = pd.merge(df_feature, pocs_distintos, on='CLAVEUC', how='left')
    df_feature = pd.merge(df_feature, contratos_total, on='CLAVEUC', how='left')
    df_feature = pd.merge(
        df_feature, monto_uc_contratos, on='CLAVEUC', how='left')
    df_feature = df_feature.fillna(0)
    return df_feature


def interaccion_sancionados(df_procs, df_sancionados, **kwargs):
    df_feature = pd.DataFrame(
        data=df_procs.CLAVEUC.unique(), columns=['CLAVEUC'])
    df = pd.merge(
        df_procs, df_sancionados, on='PROVEEDOR_CONTRATISTA', how='inner')
    monto_por_contrato = df.groupby(
        ['DEPENDENCIA', 'CLAVEUC', 'PROVEEDOR_CONTRATISTA',
         'NUMERO_PROCEDIMIENTO', 'CODIGO_CONTRATO'],
        as_index=False).IMPORTE_PESOS.sum()
    # número de proveedores fantasma por uc
    pocs_distintos = monto_por_contrato.groupby(
        'CLAVEUC').PROVEEDOR_CONTRATISTA.nunique()
    pocs_distintos = pocs_distintos.reset_index()
    pocs_distintos = pocs_distintos.rename(
        columns={'PROVEEDOR_CONTRATISTA': 'num_proveedores_sancionados'})
    # número de contratos con rfc fantasmas por uc
    contratos_total = monto_por_contrato.groupby(
        ['CLAVEUC', 'NUMERO_PROCEDIMIENTO']).CODIGO_CONTRATO.nunique()
    contratos_total = contratos_total.reset_index()
    contratos_total = contratos_total.rename(
        columns={'CODIGO_CONTRATO': 'contratos_con_sancionados'})
    contratos_total = contratos_total.groupby('CLAVEUC',
        as_index=False).contratos_con_sancionados.sum()
    # monto con rfc fantasmas por uc
    monto_uc_contratos = monto_por_contrato.groupby(
        ['CLAVEUC', 'NUMERO_PROCEDIMIENTO', 'CODIGO_CONTRATO'],
        as_index=False).IMPORTE_PESOS.sum()
    monto_uc_contratos = monto_uc_contratos.groupby(
        'CLAVEUC', as_index=False).IMPORTE_PESOS.sum()
    monto_uc_contratos = monto_uc_contratos.rename(
        columns={'IMPORTE_PESOS': 'monto_con_sancionados'})
    # join the features
    df_feature = pd.merge(df_feature, pocs_distintos, on='CLAVEUC', how='left')
    df_feature = pd.merge(df_feature, contratos_total, on='CLAVEUC', how='left')
    df_feature = pd.merge(
        df_feature, monto_uc_contratos, on='CLAVEUC', how='left')
    df_feature = df_feature.fillna(0)
    return df_feature


def porcentaje_contratos_por_convenio(df, **kwargs):
    monto_por_contrato = df.groupby(
        ['DEPENDENCIA', 'CLAVEUC', 'PROVEEDOR_CONTRATISTA',
         'NUMERO_PROCEDIMIENTO', 'CODIGO_CONTRATO', 'CONVENIO_MODIFICATORIO'],
        as_index=False).IMPORTE_PESOS.sum()
    contratos_total = monto_por_contrato.groupby(
        ['CLAVEUC', 'NUMERO_PROCEDIMIENTO',
         'CONVENIO_MODIFICATORIO']).CODIGO_CONTRATO.nunique()
    contratos_total = contratos_total.reset_index()
    contratos_total = contratos_total.groupby(
        ['CLAVEUC', 'CONVENIO_MODIFICATORIO'],
        as_index=False).CODIGO_CONTRATO.sum()
    contratos_total = contratos_total.pivot(index='CLAVEUC',
        columns='CONVENIO_MODIFICATORIO', values='CODIGO_CONTRATO')
    contratos_total = contratos_total.fillna(0)
    num_contratos = contratos_total.sum(axis=1)
    contratos_total = contratos_total.rename(
        columns={
            c: 'pc_contratos_convenio_' + c.lower().replace(' ', '_')
            for c in contratos_total.columns
        }
    )
    contratos_total = contratos_total * 100
    contratos_total = contratos_total.divide(num_contratos, axis='index')
    contratos_total.columns.name = ''
    contratos_total = contratos_total.reset_index()
    return contratos_total


def pc_licitaciones_nacionales_menor_15_dias(df, **kwargs):
    """Porcentaje de licitaciones nacionales
    cuyo plazo entre publicacion y apertura fue
    menor a 15 días"""
    df = df.copy()
    df_feature = pd.DataFrame(
        data=df.CLAVEUC.unique(), columns=['CLAVEUC'])
    # Sólo licitaciones nacionales
    tipos_validos = {'LICITACION PUBLICA',
                     'INVITACION A CUANDO MENOS TRES',
                     'LICITACION PUBLICA CON OSD'}
    df = df.loc[
        (df.CARACTER == 'NACIONAL') &
        (df.TIPO_PROCEDIMIENTO.isin(tipos_validos))
    ]
    # columnas de interés
    cols = [
        'CLAVEUC', 'NUMERO_PROCEDIMIENTO',
        'FECHA_APERTURA_PROPOSICIONES',
        'PROC_F_PUBLICACION'
    ]
    df = df.loc[:, cols].drop_duplicates()
    delta_dias = (
        df.FECHA_APERTURA_PROPOSICIONES - df.PROC_F_PUBLICACION
    ).dt.days
    df = df.assign(delta_dias=delta_dias.fillna(0))
    df = df.assign(licitaciones_menor_15=(df.delta_dias < 15))
    df = (df.groupby(['CLAVEUC', 'licitaciones_menor_15'])
            .NUMERO_PROCEDIMIENTO.nunique()
            .reset_index()
            .pivot(index='CLAVEUC',
                   columns='licitaciones_menor_15',
                   values='NUMERO_PROCEDIMIENTO')
            .rename(columns={True: 'pc_licitaciones_menor_15'}))
    valor_pc = (df.pc_licitaciones_menor_15 * 100).divide(df.sum(axis=1))
    df = (df.assign(pc_licitaciones_menor_15=valor_pc.fillna(0))
            .reset_index()
            .loc[:, ['CLAVEUC', 'pc_licitaciones_menor_15']])
    # left join
    df_feature = pd.merge(df_feature, df, on='CLAVEUC', how='left')
    df_feature = df_feature.assign(
        pc_licitaciones_menor_15=df_feature.pc_licitaciones_menor_15.fillna(0)
    )
    return df_feature


def pc_licitaciones_internacionales_menor_20_dias(df, **kwargs):
    """Porcentaje de licitaciones internacionales
    cuyo plazo entre publicacion y apertura fue
    menor a 20 días"""
    df = df.copy()
    df_feature = pd.DataFrame(
        data=df.CLAVEUC.unique(), columns=['CLAVEUC'])
    # Sólo licitaciones nacionales
    tipos_validos = {'LICITACION PUBLICA',
                     'INVITACION A CUANDO MENOS TRES',
                     'LICITACION PUBLICA CON OSD'}
    df = df.loc[
        (df.TIPO_PROCEDIMIENTO.isin(tipos_validos)) &
        (df.CARACTER.isin({'INTERNACIONAL', 'INTERNACIONAL ABIERTA'}))
    ]
    # columnas de interés
    cols = [
        'CLAVEUC', 'NUMERO_PROCEDIMIENTO',
        'FECHA_APERTURA_PROPOSICIONES',
        'PROC_F_PUBLICACION'
    ]
    df = df.loc[:, cols].drop_duplicates()
    delta_dias = (
        df.FECHA_APERTURA_PROPOSICIONES - df.PROC_F_PUBLICACION
    ).dt.days
    df = df.assign(delta_dias=delta_dias.fillna(0))
    df = df.assign(licitaciones_menor_20=(df.delta_dias < 20))
    df = (df.groupby(['CLAVEUC', 'licitaciones_menor_20'])
            .NUMERO_PROCEDIMIENTO.nunique()
            .reset_index()
            .pivot(index='CLAVEUC',
                   columns='licitaciones_menor_20',
                   values='NUMERO_PROCEDIMIENTO')
            .rename(columns={True: 'pc_licitaciones_menor_20'}))
    valor_pc = (df.pc_licitaciones_menor_20 * 100).divide(df.sum(axis=1))
    df = (df.assign(pc_licitaciones_menor_20=valor_pc.fillna(0))
            .reset_index()
            .loc[:, ['CLAVEUC', 'pc_licitaciones_menor_20']])
    # left join
    df_feature = pd.merge(df_feature, df, on='CLAVEUC', how='left')
    df_feature = df_feature.assign(
        pc_licitaciones_menor_20=df_feature.pc_licitaciones_menor_20.fillna(0)
    )
    return df_feature


def pc_licitaciones_internacionales_menor_40_dias(df, **kwargs):
    """Porcentaje de licitaciones internacionales
    bajo la cobertura de tratados cuyo plazo
    entre publicacion y apertura fue menor a 40 días"""
    df = df.copy()
    df_feature = pd.DataFrame(
        data=df.CLAVEUC.unique(), columns=['CLAVEUC'])
    # Sólo licitaciones nacionales
    tipos_validos = {'LICITACION PUBLICA',
                     'INVITACION A CUANDO MENOS TRES',
                     'LICITACION PUBLICA CON OSD'}
    df = df.loc[
        (df.TIPO_PROCEDIMIENTO.isin(tipos_validos)) &
        (df.CARACTER == 'INTERNACIONAL BAJO TLC')
    ]
    # columnas de interés
    cols = [
        'CLAVEUC', 'NUMERO_PROCEDIMIENTO',
        'FECHA_APERTURA_PROPOSICIONES',
        'PROC_F_PUBLICACION'
    ]
    df = df.loc[:, cols].drop_duplicates()
    delta_dias = (
        df.FECHA_APERTURA_PROPOSICIONES - df.PROC_F_PUBLICACION
    ).dt.days
    df = df.assign(delta_dias=delta_dias.fillna(0))
    df = df.assign(licitaciones_menor_40=(df.delta_dias < 40))
    df = (df.groupby(['CLAVEUC', 'licitaciones_menor_40'])
            .NUMERO_PROCEDIMIENTO.nunique()
            .reset_index()
            .pivot(index='CLAVEUC',
                   columns='licitaciones_menor_40',
                   values='NUMERO_PROCEDIMIENTO')
            .rename(columns={True: 'pc_licitaciones_menor_40'}))
    valor_pc = (df.pc_licitaciones_menor_40 * 100).divide(df.sum(axis=1))
    df = (df.assign(pc_licitaciones_menor_40=valor_pc.fillna(0))
            .reset_index()
            .loc[:, ['CLAVEUC', 'pc_licitaciones_menor_40']])
    # left join
    df_feature = pd.merge(df_feature, df, on='CLAVEUC', how='left')
    df_feature = df_feature.assign(
        pc_licitaciones_menor_40=df_feature.pc_licitaciones_menor_40.fillna(0)
    )
    return df_feature


def diferente_estratificacion(df, **kwargs):
    df = df.copy()
    cols = [
        'CLAVEUC', 'PROVEEDOR_CONTRATISTA',
        'NUMERO_PROCEDIMIENTO',
        'CODIGO_EXPEDIENTE', 'CODIGO_CONTRATO'
    ]
    df = df.drop_duplicates(subset=cols)
    df = df.loc[:, cols + ['ESTRATIFICACION_MUC', 'ESTRATIFICACION_MPC']]
    estratificacion_igual = df.ESTRATIFICACION_MUC == df.ESTRATIFICACION_MPC
    df = df.assign(estratificacion_igual=estratificacion_igual)
    df_feature = (df.groupby(['CLAVEUC', 'estratificacion_igual'], as_index=False)
                  .PROVEEDOR_CONTRATISTA.count())
    df_feature = df_feature.pivot(index='CLAVEUC',
                                  columns='estratificacion_igual',
                                  values='PROVEEDOR_CONTRATISTA')
    df_feature = (df_feature * 100).divide(df_feature.sum(axis=1), axis=0)
    df_feature = df_feature.fillna(0)
    if False not in df_feature.columns:
        raise ValueError('Todos reportaron su valor correctamente')

    col_feature = 'pc_estratificacion_mal_reportada'
    df_feature = df_feature.rename(columns={False: col_feature})
    df_feature = (df_feature.reset_index()
                  .loc[:, ['CLAVEUC', col_feature]])
    df_feature.columns.name = ''
    return df_feature


def pc_rotacion_top_proveedores(df: DataFrame,
                                first_period: Tuple[int]=(2012, 2013),
                                second_period: Tuple[int]=(2015, 2016),
                                top_pc: float=20):
    """Tabla de procedimientos. La rotacion puede no ser tan buena.
    Tomar el top 20%"""
    df: DataFrame = df.copy()
    claves: DataFrame = pd.DataFrame(df.CLAVEUC.unique(),
                                     columns=['CLAVEUC'])
    df = df.assign(Year=df.FECHA_INICIO.dt.year)
    cols = ['CLAVEUC', 'PROVEEDOR_CONTRATISTA', 'Year']
    montos = df.groupby(cols, as_index=False).IMPORTE_PESOS.sum()
    # montos = montos.loc[montos.Year.isin({first_year, second_year})]
    df_first = montos.loc[montos.Year.isin(first_period)]
    df_second = montos.loc[montos.Year.isin(second_period)]
    monto_total_first = (df_first.groupby('CLAVEUC', as_index=False)
                                 .IMPORTE_PESOS.sum()
                                 .rename(columns={'IMPORTE_PESOS': 'MONTO_TOTAL'}))
    monto_total_second = (df_second.groupby('CLAVEUC', as_index=False)
                                   .IMPORTE_PESOS.sum()
                                   .rename(columns={'IMPORTE_PESOS': 'MONTO_TOTAL'}))
    df_first = pd.merge(df_first, monto_total_first,
                        on='CLAVEUC', how='inner')
    df_second = pd.merge(df_second, monto_total_second,
                         on='CLAVEUC', how='inner')
    df_first = df_first.assign(
        pc_monto=df_first.IMPORTE_PESOS.divide(df_first.MONTO_TOTAL)
    ).drop(['IMPORTE_PESOS', 'MONTO_TOTAL', 'Year'], axis=1)
    df_second = df_second.assign(
        pc_monto=df_second.IMPORTE_PESOS.divide(df_second.MONTO_TOTAL)
    ).drop(['IMPORTE_PESOS', 'MONTO_TOTAL', 'Year'], axis=1)
    # TODO: se me hace raro que sea 20
    threshold = top_pc / 100
    group_first = []
    for group, subdf in df_first.groupby('CLAVEUC'):
        df_aux = subdf.sort_values('pc_monto', ascending=False)
        df_aux = df_aux.assign(pc_monto_cumsum=df_aux.pc_monto.cumsum())
        df_aux = df_aux.loc[df_aux.pc_monto_cumsum <= threshold]
        if df_aux.shape[0] == 0:
            df_aux = df_aux.iloc[0:1, :]
        proveedores = set(df_aux.PROVEEDOR_CONTRATISTA.unique())
        result = {'CLAVEUC': group, 'proveedores_first': proveedores}
        group_first.append(result)
    group_second = []
    for group, subdf in df_second.groupby('CLAVEUC'):
        df_aux = subdf.sort_values('pc_monto', ascending=False)
        df_aux = df_aux.assign(pc_monto_cumsum=df_aux.pc_monto.cumsum())
        df_aux = df_aux.loc[df_aux.pc_monto_cumsum <= threshold]
        if df_aux.shape[0] == 0:
            df_aux = df_aux.iloc[0:1, :]
        proveedores = set(df_aux.PROVEEDOR_CONTRATISTA.unique())
        result = {'CLAVEUC': group, 'proveedores_second': proveedores}
        group_second.append(result)

    df_first = pd.DataFrame(group_first)
    df_second = pd.DataFrame(group_second)
    df_final = pd.merge(claves, df_first, on='CLAVEUC', how='left')
    df_final = pd.merge(df_final, df_second, on='CLAVEUC', how='left')
    proveedores_first = df_final.proveedores_first.mask(
        df_final.proveedores_first.isnull(), set()
    )
    proveedores_second = df_final.proveedores_second.mask(
        df_final.proveedores_second.isnull(), set()
    )
    df_final = df_final.assign(
        proveedores_first=proveedores_first,
        proveedores_second=proveedores_second
    )
    output = []
    for row in df_final.itertuples():
        num = len(row.proveedores_first & row.proveedores_second)
        if len(row.proveedores_first) == 0:
            # TODO revisar caso default
            pc_continuidad = 1
        else:
            pc_continuidad = num / len(row.proveedores_first)
        pc_rotacion = 1 - pc_continuidad
        output.append({'CLAVEUC': row.CLAVEUC,
                       'pc_rotacion_top_proveedores': pc_rotacion})
    df_final = pd.merge(pd.DataFrame(output), df_final, on='CLAVEUC', how='inner')
    return df_final


# Requiere la tabla de máximos


def porcentaje_adjudicaciones_excedieron_monto(df, df_maximos,  **kwargs):
    # df > df_procs_<tipo>
    # df_maximos es tipos maximos
    if 'tipo_contratacion' in kwargs:
        tipo_contratacion = kwargs['tipo_contratacion']
    else:
        raise TypeError('Falta especificar tipo_contratacion')
    años_validos = set(range(2012, 2017))
    df_maximos = df_maximos.loc[
        (df_maximos.Año.isin(años_validos)) &
        (df_maximos['Tipo de contratación'] == tipo_contratacion)
    ]
    df_maximos = df_maximos.drop(['Tipo de contratación', 'INV3'], axis=1)
    df = df.copy()
    df_claves = pd.DataFrame(
        data=df.CLAVEUC.unique(), columns=['CLAVEUC'])
    # Sólo ADJUDICACION DIRECTA
    df = df.loc[df.TIPO_PROCEDIMIENTO == 'ADJUDICACION DIRECTA']
    df = df.assign(Año=df.FECHA_INICIO.dt.year)
    df = df.loc[df.Año.isin(años_validos)]
    monto_por_contrato = df.groupby(
        ['CLAVEUC', 'Año', 'PROVEEDOR_CONTRATISTA',
         'NUMERO_PROCEDIMIENTO', 'CODIGO_CONTRATO'],
        as_index=False
    ).IMPORTE_PESOS.sum()
    monto_por_proc = monto_por_contrato.groupby(
        ['CLAVEUC', 'Año', 'NUMERO_PROCEDIMIENTO'], as_index=False
    ).IMPORTE_PESOS.sum()
    monto_por_proc = pd.merge(monto_por_proc, df_maximos, on='Año', how='inner')
    es_mayor_al_max = monto_por_proc.IMPORTE_PESOS > monto_por_proc['Adjudicación directa']
    monto_por_proc = monto_por_proc.assign(es_mayor_al_max=es_mayor_al_max)

    monto_por_proc = (monto_por_proc.groupby(['CLAVEUC', 'Año', 'es_mayor_al_max'])
                      .NUMERO_PROCEDIMIENTO.nunique()
                      .reset_index()
                      .pivot_table(index=['CLAVEUC', 'Año'],
                                   columns=['es_mayor_al_max'],
                                   values='NUMERO_PROCEDIMIENTO')
                      .rename(columns={True: 'num_excedidas_si',
                                       False: 'num_excedidas_no'})
                      .fillna(0))
    pc_adj_directas_excedidas = monto_por_proc.num_excedidas_si.divide(monto_por_proc.sum(axis=1))
    monto_por_proc = (monto_por_proc.assign(pc_adj_directas_excedidas=pc_adj_directas_excedidas * 100)
                      .reset_index()
                      .pivot(index='CLAVEUC',
                             columns='Año',
                             values='pc_adj_directas_excedidas')
                      .fillna(0)
                      .assign(pc_adj_excedidas_prom=lambda data: data.mean(axis=1))
                      .drop(años_validos, axis=1)
                      .reset_index())
    # left join
    df_feature = pd.merge(df_claves, monto_por_proc,
                          on='CLAVEUC', how='left')
    df_feature = df_feature.assign(
        pc_adj_excedidas_prom=df_feature.pc_adj_excedidas_prom.fillna(0)
    )
    return df_feature


def porcentaje_invitaciones_excedieron_monto(df, df_maximos, **kwargs):
    # df > df_procs_<tipo>
    # df_maximos es tipos maximos
    if 'tipo_contratacion' in kwargs:
        tipo_contratacion = kwargs['tipo_contratacion']
    else:
        raise TypeError('Falta especificar tipo_contratacion')
    años_validos = set(range(2012, 2017))
    df_maximos = df_maximos.loc[
        (df_maximos.Año.isin(años_validos)) &
        (df_maximos['Tipo de contratación'] == tipo_contratacion)
        ]
    df_maximos = df_maximos.drop(['Tipo de contratación', 'Adjudicación directa'],
                                 axis=1)
    df = df.copy()
    df_claves = pd.DataFrame(
        data=df.CLAVEUC.unique(), columns=['CLAVEUC'])
    # Sólo INV3
    df = df.loc[df.TIPO_PROCEDIMIENTO == 'INVITACION A CUANDO MENOS TRES']
    df = df.assign(Año=df.FECHA_INICIO.dt.year)
    df = df.loc[df.Año.isin(años_validos)]
    monto_por_contrato = df.groupby(
        ['CLAVEUC', 'Año', 'PROVEEDOR_CONTRATISTA',
         'NUMERO_PROCEDIMIENTO', 'CODIGO_CONTRATO'],
        as_index=False
    ).IMPORTE_PESOS.sum()
    monto_por_proc = monto_por_contrato.groupby(
        ['CLAVEUC', 'Año', 'NUMERO_PROCEDIMIENTO'], as_index=False
    ).IMPORTE_PESOS.sum()
    monto_por_proc = pd.merge(monto_por_proc, df_maximos, on='Año', how='inner')
    es_mayor_al_max = monto_por_proc.IMPORTE_PESOS > monto_por_proc['INV3']
    monto_por_proc = monto_por_proc.assign(es_mayor_al_max=es_mayor_al_max)

    monto_por_proc = (monto_por_proc.groupby(['CLAVEUC', 'Año', 'es_mayor_al_max'])
                      .NUMERO_PROCEDIMIENTO.nunique()
                      .reset_index()
                      .pivot_table(index=['CLAVEUC', 'Año'],
                                   columns=['es_mayor_al_max'],
                                   values='NUMERO_PROCEDIMIENTO')
                      .rename(columns={True: 'num_excedidas_si',
                                       False: 'num_excedidas_no'})
                      .fillna(0))
    pc_inv3_excedidas = monto_por_proc.num_excedidas_si.divide(monto_por_proc.sum(axis=1))
    monto_por_proc = (monto_por_proc.assign(pc_inv3_excedidas=pc_inv3_excedidas * 100)
                      .reset_index()
                      .pivot(index='CLAVEUC',
                             columns='Año',
                             values='pc_inv3_excedidas')
                      .fillna(0)
                      .assign(pc_inv3_excedidas_prom=lambda data: data.mean(axis=1))
                      .drop(años_validos, axis=1)
                      .reset_index())
    # left join
    df_feature = pd.merge(df_claves, monto_por_proc,
                          on='CLAVEUC', how='left')
    df_feature = df_feature.assign(
        pc_inv3_excedidas_prom=df_feature.pc_inv3_excedidas_prom.fillna(0)
    )
    return df_feature


# Features scraper

def promedio_convenios_por_proc(df, **kwargs):
    """Usa tabla scraper.
    Calcula el promedio de contratos modificatorios por
    procedimiento"""
    df = df.copy()
    df_convenios_prom = (df.loc[df.numero_convenios > 0]
                           .groupby('CLAVEUC').numero_convenios.mean())
    df_feature = pd.merge(df.loc[:, ['CLAVEUC']].drop_duplicates(),
                          df_convenios_prom.reset_index(),
                          on='CLAVEUC', how='left')
    df_feature = df_feature.rename(
        columns={'numero_convenios': 'promedio_convenios'})
    df_feature = df_feature.assign(
        promedio_convenios=df_feature.promedio_convenios.fillna(0))
    return df_feature


def porcentaje_procs_sin_convocatoria(df, tipos_validos=None, **kwargs):
    """Usa tabla scraper.
    Calcula el porcentaje de procedimientos sin archivo de convocatoria"""
    if tipos_validos is None:
        # solo aplica para INV a 3 y Licitaciones publicas
        tipos_validos = {
            'INVITACION A CUANDO MENOS TRES',
            'LICITACION PUBLICA',
            'LICITACION PUBLICA CON OSD'
        }
    df_claves = pd.DataFrame(
        data=df.CLAVEUC.unique(), columns=['CLAVEUC'])
    df = df.loc[df.TIPO_PROCEDIMIENTO.isin(tipos_validos)].copy()
    df_feature = (df.groupby(['CLAVEUC', 'archivo_convocatoria'],
                             as_index=False).CODIGO_EXPEDIENTE.count()
                    .pivot(index='CLAVEUC', columns='archivo_convocatoria',
                           values='CODIGO_EXPEDIENTE')
                    .fillna(0)
                    .rename(columns={0: 'pc_sin_convocatoria'}))
    columnas = list(df_feature.columns.values)
    if 'pc_sin_convocatoria' not in columnas:
        raise ValueError('Todos los procedimientos tienen '
                         'archivo de convocatoria')
    df_feature = (df_feature * 100).divide(df_feature.sum(axis=1), axis=0)
    df_feature = (df_feature.reset_index()
                            .loc[:, ['CLAVEUC', 'pc_sin_convocatoria']])
    df_feature.columns.name = ''
    df_feature = pd.merge(df_claves, df_feature, on='CLAVEUC', how='left')
    df_feature = df_feature.fillna(0)
    return df_feature


# Tabla de participantes

def ganadores_por_participantes(df: DataFrame) -> DataFrame:
    """Tabla de participantes. """
    df = df.copy()
    # Se sacan los procedimientos que sí se realizaron
    df_participantes = df.loc[df.ESTATUS_FALLO == 'GANADOR']
    estatus = df_participantes.ESTATUS_DE_PROPUESTA.mask(
        df_participantes.ESTATUS_DE_PROPUESTA == 'SIN REPORTAR', 'GANADOR'
    )
    df_participantes = df_participantes.assign(ESTATUS_DE_PROPUESTA=estatus)
    df_num_part = (df_participantes.groupby('CLAVEUC')
                                   .PROVEEDOR_CONTRATISTA.nunique()
                                   .reset_index())
    df_num_part = df_num_part.rename(
        columns={'PROVEEDOR_CONTRATISTA': 'num_participantes'})
    df_ganadores = df_participantes.loc[
        df_participantes.ESTATUS_DE_PROPUESTA == 'GANADOR']
    df_ganadores = (df_ganadores.groupby('CLAVEUC')
                                .PROVEEDOR_CONTRATISTA.nunique()
                                .reset_index())
    df_ganadores = df_ganadores.rename(
        columns={'PROVEEDOR_CONTRATISTA': 'num_ganadores'})
    df_final = pd.merge(df_num_part, df_ganadores,
                        on='CLAVEUC', how='inner')
    feature = df_final.num_ganadores.divide(df_final.num_participantes)
    df_final = df_final.assign(ganadores_por_participantes=feature)
    df_feature = df_final.loc[:, ['CLAVEUC', 'ganadores_por_participantes']]
    return df_feature

