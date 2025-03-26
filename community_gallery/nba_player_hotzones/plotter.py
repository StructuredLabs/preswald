import numpy as np
import plotly.graph_objects as go
import sys
import os
import plotly as px
sys.path.append(os.path.abspath(os.getcwd()))

from constants import Areas, Ranges


def drawCenterZones(fig, centerEfficiency):
    
    # color
    efficiency3pt = round(centerEfficiency[Ranges.MORE_24_FT.value.idx], 2)
    r3pt = min(255, efficiency3pt * 500)
    b3pt = 255 - r3pt
    rectX = [2,2,4,4]
    rectY = [0,4,4,0]
    fig.add_trace(
         go.Scatter(
            x=rectX,
            y=rectY,
            mode="lines",
            fill="toself",
            fillcolor=f'rgb({r3pt}, 0, {b3pt})',
            hoverinfo="text",
            text=f'FG%: {efficiency3pt}%'
        )
    )

    theta = np.linspace(7 * np.pi / 6, 11 * np.pi / 6, 100)
    closeX = 3 + 1.8 * np.cos(theta)
    closeY = 3.8 + 1.2 * np.sin(theta)
    rCloseRectX = [1.4412, 1.4412, 4.5588, 4.5588, 1.4412]
    rCloseRectY = [3.2, 4, 4, 3.2, 3.2]
    
    #Color 
    efficiencyClose = round(centerEfficiency[Ranges.LESS_8_FT.value.idx], 2)
    rClose = min(255, efficiencyClose * 400)
    bClose = 255 - rClose
    fig.add_trace(
        go.Scatter(
            x=rCloseRectX,
            y=rCloseRectY,
            mode="lines",
            fill="toself",
            fillcolor=f'rgb({rClose}, 0, {bClose})',
            hoverinfo="text",
            text=f'FG%: {efficiencyClose}%'
        )
    )
    fig.add_trace(
        go.Scatter(
            x=closeX,
            y=closeY,
            mode="lines",
            fill="toself",
            fillcolor=f'rgb({rClose}, 0, {bClose})',
            hoverinfo="text",
             text=f'FG%: {efficiencyClose}%'
        )
    )

    medTopSemiX = 3 + 1.2 * np.cos(theta)
    medTopSemiY = 3.025 + 0.4 * np.sin(theta)
    medBottomSemiY = 2.2 + 0.4 * np.sin(theta)
    fig.add_trace(
        go.Scatter(
            x=medTopSemiX,
            y=medTopSemiY,
            mode="lines",
            fill="toself",
            fillcolor=f'rgb({rClose}, 0, {bClose})',
            hoverinfo='text',
            text=f'FG%: {efficiencyClose}%',
        )
    )
    
    #color 
    medEfficiency = round(centerEfficiency[Ranges.BETWEEN_8_16_FT.value.idx], 2)
    rMed =  min(255,  medEfficiency * 400)
    bMed = 255 - rMed
    rectX = [2,2,4,4]
    rectY = [2,2.8,2.8,2]
    fig.add_trace(
        go.Scatter(
            x=rectX,
            y=rectY,
            mode="lines",
            fill="toself",
            fillcolor=f'rgb({rMed}, 0, {bMed})',
            hoverinfo='text',
            text=f'FG%: {medEfficiency}%',
        )
    )


    longTopSemiX = 3 + 1.2 * np.cos(theta)
    longTopSemiY = 2.2 + 0.4 * np.sin(theta)
    longBottomSemiY = 1 + 0.4 * np.sin(theta)
    fig.add_trace(
        go.Scatter(
            x=longTopSemiX,
            y=longTopSemiY,
            mode="lines",
            fill="toself",
            fillcolor=f'rgb({rMed}, 0, {bMed})',
            hoverinfo='text',
            text=f'FG%: {medEfficiency}%',
        )
    )
    
    efficiencyFar = round(centerEfficiency[Ranges.BETWEEN_16_24_FT.value.idx] , 2)
    rFar =  min(255, efficiencyFar * 500)
    bFar = 255 - rFar

    rectX = [2,2,4,4]
    rectY = [0.78,2,2,0.78]
    fig.add_trace(
        go.Scatter(
            x=rectX,
            y=rectY,
            mode="lines",
            fill="toself",
            fillcolor=f'rgb({rFar}, 0, {bFar})',
            hoverinfo='text',
            text=f'FG%: {efficiencyFar}%',
        )
    )
    fig.add_trace(
        go.Scatter(
            x=longTopSemiX,
            y=longBottomSemiY,
            mode="lines",
            fill="toself",
            fillcolor=f'rgb({rFar}, 0, {bFar})',
            hoverinfo='text',
            text=f'FG%: {efficiencyFar}%',
        )
    )
    
    
    fig.add_trace(
        go.Scatter(
            x=medTopSemiX,
            y=medBottomSemiY,
            mode="lines",
            fill="toself",
            fillcolor=f'rgb({rMed}, 0, {bMed})',
            hoverinfo='text',
            text=f'FG%: {medEfficiency}%',
        )
    )


def drawUpperLeftZones(fig, leftEfficiency):
    
    efficiency3pt = round(leftEfficiency[Ranges.MORE_24_FT.value.idx], 2)
    r3pt =  min(255, efficiency3pt * 500)
    b3pt = 255 - r3pt
    x3pt = [0, 3.4, 0, 0]
    y3pt = [2.6, 4, 4, 2.6]
    fig.add_trace(
        go.Scatter(
            x=x3pt,
            y=y3pt,
            mode="lines",
            fill="toself",
            fillcolor=f'rgb({r3pt}, 0, {b3pt})',
            hoverinfo='text',
            text=f'FG%: {efficiency3pt}%',
        )
    )
    
    efficiencyFar = round(leftEfficiency[Ranges.BETWEEN_16_24_FT.value.idx], 2)
    rFar =  min(255, efficiencyFar * 400)
    bFar = 255 - rFar
    

    xFar = [0.5, 3.2, 0.5, 0.5]
    yFar = [2.8, 4, 4, 2.8]
    fig.add_trace(
        go.Scatter(
            x=xFar,
            y=yFar,
            mode="lines",
            fill="toself",
            fillcolor=f'rgb({rFar}, 0, {bFar})',
            hoverinfo="text",
            text=f'FG%: {efficiencyFar}%',
        )
    )
    efficiencyMed = round(leftEfficiency[Ranges.BETWEEN_8_16_FT.value.idx], 2)
    rMed=  min(255, efficiencyMed * 400)
    bMed = 255 - rMed

    xMed = [1, 3.3, 1, 1]
    yMed = [3, 4, 4, 3]
    fig.add_trace(
        go.Scatter(
            x=xMed,
            y=yMed,
            mode="lines",
            fill="toself",
            fillcolor=f'rgb({rMed}, 0, {bMed})',
            hoverinfo="text",
            text=f'FG%: {efficiencyMed}',
        )
    )


def drawUpperRightZones(fig, rightEfficiency):
    efficiency3pt = round(rightEfficiency[Ranges.MORE_24_FT.value.idx], 2)
    r3pt =  min(255, efficiency3pt * 500)
    b3pt = 255 - r3pt
    x3pt = [6, 2.6, 6, 6]
    y3pt = [2.6, 4, 4, 2.6]
    fig.add_trace(
        go.Scatter(
            x=x3pt,
            y=y3pt,
            mode="lines",
            fill="toself",
            fillcolor=f'rgb({r3pt}, 0, {b3pt})',
            hoverinfo="text",
            text=f'FG%: {efficiency3pt}',
        )
    )
    efficiencyFar = round(rightEfficiency[Ranges.BETWEEN_16_24_FT.value.idx], 2)
    rFar =  min(255, efficiencyFar * 400)
    bFar = 255 - rFar
    
    xFar = [5.5, 2.8, 5.5, 5.5]
    yFar = [2.8, 4, 4, 2.8]

    fig.add_trace(
        go.Scatter(
            x=xFar,
            y=yFar,
            mode="lines",
            fill="toself",
            fillcolor=f'rgb({rFar}, 0, {bFar})',
            hoverinfo="text",
            text=f'FG%: {efficiencyFar}',
        )
    )

    efficiencyMed = round(rightEfficiency[Ranges.BETWEEN_8_16_FT.value.idx], 2)
    rMed=  min(255, efficiencyMed * 400)
    bMed = 255 - rMed
    xMed = [5, 2.7, 5, 5]
    yMed = [3, 4, 4, 3]

    fig.add_trace(
        go.Scatter(
            x=xMed,
            y=yMed,
            mode="lines",
            fill="toself",
            fillcolor=f'rgb({rMed}, 0, {bMed})',
            hoverinfo="text",
            text=f'FG%: {efficiencyMed}',
        )
    )


def drawLeftCenterZones(fig, leftCenterEfficiency):
    efficiency3pt = round(leftCenterEfficiency[Ranges.MORE_24_FT.value.idx], 2)
    r3pt =  min(255, efficiency3pt * 400)
    b3pt = 255 - r3pt
    
    x3pt = [2, 2, 0, 0, 2]
    y3pt = [3.5, 0, 0, 2.6, 3.5]
    fig.add_trace(
        go.Scatter(
            x=x3pt,
            y=y3pt,
            mode="lines",
            fill="toself",
            fillcolor=f'rgb({r3pt}, 0, {b3pt})',
            hoverinfo="text",
            text=f'FG%: {efficiency3pt}',
        )
    )

    theta = np.linspace(np.pi, 4 * np.pi / 3, 50)
    theta2 = np.linspace(np.pi, 4.3, 50)[::-1]
    theta3 = np.linspace(3.38, 3.9, 50)[::-1]

    xFar = np.concatenate([3 + 2 * np.cos(theta), [2], 3 + 2.5 * np.cos(theta2), [0.5], [1]])
    yFar = np.concatenate(
        [3 + 1.2 * np.sin(theta), [0.78], 2.6 + 2 * np.sin(theta2), [2.8], [3]]
    )

    efficiencyFar = round(leftCenterEfficiency[Ranges.BETWEEN_16_24_FT.value.idx], 2)
    rFar =  min(255, efficiencyFar * 400)
    bFar = 255 - rFar
    
    fig.add_trace(
        go.Scatter(
            x=xFar,
            y=yFar,
            mode="lines",  # Only show the outline
            fill='toself',
            fillcolor=f'rgb({rFar}, 0, {bFar})',
            hoverinfo="text",
            text=f'FG%: {efficiencyFar}',
        )
    )

    
    efficiencyMed = round(leftCenterEfficiency[Ranges.BETWEEN_8_16_FT.value.idx], 2)
    rMed=  min(255, efficiencyMed * 400)
    bMed = 255 - rMed
    xMed = np.concatenate([3 + 2 * np.cos(theta), [2], 3.6 + 2.2 * np.cos(theta3)])
    yMed = np.concatenate([3 + 1.2 * np.sin(theta), [2.8], 3.4 + 0.85 * np.sin(theta3)])
    fig.add_trace(
        go.Scatter(
            x=xMed,
            y=yMed,
            mode="lines",
            fill="toself",
            fillcolor=f'rgb({rMed}, 0, {bMed})',
            hoverinfo="text",
            text=f'FG%: {efficiencyMed}',
        )
    )
    


def drawRightCenterZones(fig, rightCenterEfficiency):
    efficiency3pt = round(rightCenterEfficiency[Ranges.MORE_24_FT.value.idx], 2)
    r3pt =  min(255, efficiency3pt * 500)
    b3pt = 255 - r3pt
    x3pt = [4, 4, 6, 6, 4]
    y3pt = [3.5, 0, 0, 2.6, 3.5]
    fig.add_trace(
        go.Scatter(
            x=x3pt,
            y=y3pt,
            mode="lines",
            fill="toself",
            fillcolor=f'rgb({r3pt}, 0, {b3pt})',
            hoverinfo="text",
            text=f'FG%: {efficiency3pt}',
        )
    )

    theta = np.linspace(5 * np.pi / 3, 2 * np.pi, 50)
    theta2 = np.linspace(5.13, 2 * np.pi, 50)[::-1]
    theta3 = np.linspace(10.55 * np.pi / 6, 11.6 * np.pi / 6, 50)

    xFar = np.concatenate(
        [3 + 2 * np.cos(theta), [5.5], [5.5], 3 + 2.5 * np.cos(theta2), [4]]
    )
    yFar = np.concatenate(
        [3 + 1.2 * np.sin(theta), [2.8], [2.6], 2.6 + 2 * np.sin(theta2), [2]]
    )

    efficiencyFar = round(rightCenterEfficiency[Ranges.BETWEEN_16_24_FT.value.idx], 2)
    rFar =  min(255, efficiencyFar * 400)
    bFar = 255 - rFar
    fig.add_trace(
        go.Scatter(
            x=xFar,
            y=yFar,
            mode="lines",
            line=dict(color="black", width=3),
            fill="toself",
            fillcolor=f'rgb({rFar}, 0, {bFar})',
            hoverinfo="text",
            text=f'FG%: {efficiencyFar}',
        )
    )
    
    xMed = np.concatenate(
        [2.4 + 2.2 * np.cos(theta3), [5], (3 + 2 * np.cos(theta))[::-1], [4]]
    )
    yMed = np.concatenate(
        [3.4 + 0.85 * np.sin(theta3), [3], (3 + 1.2 * np.sin(theta))[::-1], [2.7]]
    )
    
    efficiencyMed = round(rightCenterEfficiency[Ranges.BETWEEN_8_16_FT.value.idx], 2)
    rMed=  min(255, efficiencyMed * 400)
    bMed = 255 - rMed
    fig.add_trace(
        go.Scatter(
            x=xMed,
            y=yMed,
            mode="lines",
            fill="toself",
            fillcolor=f'rgb({rMed}, 0, {bMed})',
            hoverinfo="text",
            text=f'FG%: {efficiencyMed}',
        )
    )


def drawCourtLines(fig):
    theta = np.linspace(np.pi, 2 * np.pi, 50)
    #Border
    fig.add_shape(
        type="rect", x0=0, y0=0, x1=6, y1=4, line=dict(color="black", width=5)
    )

    #Key 
    fig.add_shape(
        type="rect", x0=2, y0=2, x1=4, y1=4, line=dict(color="black", width=2)
    )

    freeThrowX = 3 + np.cos(theta)
    freeThrowY = 2 + np.sin(theta)

    # Free throw 
    fig.add_trace(
        go.Scatter(
            x=freeThrowX, y=freeThrowY, mode="lines", line=dict(color="black", width=3), hoverinfo='none'
        )
    )

    # Hoop
    fig.add_shape(
        type="circle",
        x0=2.8,
        y0=3.6,
        x1=3.25,
        y1=3.92,
        line=dict(color="orange", width=4),
    )
    
    
    # Backboard
    fig.add_shape(
        type="line", x0=2.5, y0=3.95, x1=3.5, y1=3.95, line=dict(color="black", width=3)
    )

    # Three-point line
    threePointX = 3 + 2.5 * np.cos(theta)
    threePointY = 2.6 + 2 * np.sin(theta)
    
    
    x=[0.5, 0.5]
    y=[2.6,4]
    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode="lines",
            fill="toself",
            hoverinfo="none",
            line=dict(color='black', width=3)
        )
    )
    
    x=[5.5, 5.5]
    y=[2.6,4]
    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode="lines",
            fill="toself",
            hoverinfo="none",
            line=dict(color='black', width=3)
        )
    )

    x=[1.4412, 1.4412]
    y=[3.2,4]
    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode="lines",
            fill="toself",
            hoverinfo="none",
            line=dict(color='black', width=3)
        )
    )
    
    x=[4.5588, 4.5588]
    y=[3.2,4]
    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode="lines",
            fill="toself",
            hoverinfo="none",
            line=dict(color='black', width=3)
        )
    )

    x = [5,5]
    y = [3,4]
    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode="lines",
            fill="toself",
            hoverinfo="none",
            line=dict(color='black', width=3)
        )
    )
    
    x = [1,1]
    y = [3,4]
    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode="lines",
            fill="toself",
            hoverinfo="text",
            line=dict(color='black', width=3)
        )
    )

    # # connect close to medium range
    fig.add_shape(
        type="line", x0=4.5558, y0=3.2, x1=6, y1=2.6, line=dict(color="gray", width=3)
    )
    fig.add_shape(
        type="line", x0=1.4412, y0=3.2, x1=0, y1=2.6, line=dict(color="gray", width=3)
    )
    fig.add_shape(
        type="line", x0=2, y0=2.8, x1=2, y1=0, line=dict(color="gray", width=3)
    )
    fig.add_shape(
        type="line", x0=4, y0=2.8, x1=4, y1=0, line=dict(color="gray", width=3)
    )

    threePointY = 2.6 + 2 * np.sin(theta)

    fig.add_trace(
        go.Scatter(
            x=threePointX,
            y=threePointY,
            mode="lines",
            line=dict(color="black", width=3),
            hoverinfo='text',
            text=''
        )
    )
    
    
    medX = 3 + 2 * np.cos(theta)
    medY = 3 + 1.2 * np.sin(theta)
    fig.add_trace(
        go.Scatter(x=medX, y=medY, mode="lines", line=dict(color="gray", width=3), hoverinfo='text', text='')
    )


def drawCourt(shootingEfficiency : dict):
    # Court boundaries
    layout = go.Layout(
        width=800,
        height=600,
        
    )

    fig = go.Figure(layout=layout)
    
    drawUpperRightZones(fig, shootingEfficiency[Areas.R.value])
    drawUpperLeftZones(fig, shootingEfficiency[Areas.L.value])
    drawRightCenterZones(fig, shootingEfficiency[Areas.RC.value])
    drawLeftCenterZones(fig, shootingEfficiency[Areas.LC.value])
    drawCenterZones(fig,  shootingEfficiency[Areas.C.value])
    drawCourtLines(fig)
    
    for trace in fig.data:
        trace.showlegend=False

    # Dummy heatmap for scale
    fig.add_trace(go.Heatmap(
    z=[[0, 1]],
    colorscale=[
        [0.0, "blue"],
        [0.5, "purple"],
        [1.0, "red"] ], 
    showscale=True,  
    colorbar=dict(
        titleside="right",
        tickmode="array",
        tickvals=[0, 0.5, 1],
        ticktext=["Cold", "Ok", "HOT!"]
    ),
    x=[None],
    y=[None]
))
    

    return fig