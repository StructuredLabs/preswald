import matplotlib.pyplot as plt
import numpy as np

from preswald import matplotlib, slider, text

# Title
text("# Matplotlib Functionality Test")

# Slider for frequency adjustment
freq_slider = slider("Wave Frequency", min_val=0.5, max_val=5.0, default=1.0, step=0.1)
frequency = freq_slider.get("value", 1.0)

# Generate data
x = np.linspace(0, 10, 100)
y_sin = np.sin(frequency * x)
y_cos = np.cos(frequency * x)

fig1, ax1 = plt.subplots()
ax1.plot(x, y_sin, label="sin", linestyle="-", marker="")
ax1.plot(x, y_cos, label="cos", linestyle="-", marker="")
ax1.set_title("Line Plot")
ax1.set_xlabel("x")
ax1.set_ylabel("y")
ax1.legend()
matplotlib(fig1)

fig2, ax2 = plt.subplots()
ax2.scatter(x, y_sin, label="sin", marker="o", color="blue")
ax2.scatter(x, y_cos, label="cos", marker="x", color="red")
ax2.set_title("Scatter Plot")
ax2.set_xlabel("x")
ax2.set_ylabel("y")
ax2.legend()
matplotlib(fig2)

fig3, ax3 = plt.subplots()
ax3.bar(x, y_sin, width=0.01, label="sin", color="blue")
ax3.bar(x, y_cos, width=0.01, label="cos", color="red", alpha=0.5)
ax3.set_title("Bar Plot")
ax3.set_xlabel("x")
ax3.set_ylabel("y")
ax3.legend()
matplotlib(fig3)

fig4, ax4 = plt.subplots()
ax4.hist(y_sin, bins=30, label="sin", color="blue", alpha=0.7)
ax4.hist(y_cos, bins=30, label="cos", color="red", alpha=0.7)
ax4.set_title("Histogram")
ax4.set_xlabel("y")
ax4.set_ylabel("Frequency")
ax4.legend()
matplotlib(fig4)

fig5, ax5 = plt.subplots()
ax5.step(x, y_sin, label="sin", where="mid", color="blue")
ax5.step(x, y_cos, label="cos", where="mid", color="red")
ax5.set_title("Step Plot")
ax5.set_xlabel("x")
ax5.set_ylabel("y")
ax5.legend()
matplotlib(fig5)

fig6, ax6 = plt.subplots()
y_sin_avg = np.mean(np.abs(y_sin))
y_cos_avg = np.mean(np.abs(y_cos))
ax6.pie(
    [y_sin_avg, y_cos_avg],
    labels=["sin", "cos"],
    colors=["blue", "red"],
    autopct="%1.1f%%",
)
ax6.set_title("Pie Chart")
matplotlib(fig6)

fig7, ax7 = plt.subplots()
ax7.boxplot(
    [y_sin, y_cos],
    labels=["sin", "cos"],
    patch_artist=True,
    boxprops=dict(facecolor="blue", color="blue"),
    medianprops=dict(color="red"),
)
ax7.set_title("Box Plot")
ax7.set_ylabel("y")
matplotlib(fig7)

fig8, ax8 = plt.subplots()
ax8.violinplot([y_sin, y_cos], showmeans=True, showmedians=True)
ax8.set_xticks([1, 2])
ax8.set_xticklabels(["sin", "cos"])
ax8.set_title("Violin Plot")
ax8.set_ylabel("y")
matplotlib(fig8)

fig9, ax9 = plt.subplots()
X, Y = np.meshgrid(x, x)
Z = np.sin(np.sqrt(X**2 + Y**2))
contour = ax9.contourf(X, Y, Z, levels=20, cmap="viridis")
cbar = fig9.colorbar(contour)
cbar.ax.set_yscale("linear")
ax9.set_title("Contour Plot")
ax9.set_xlabel("x")
ax9.set_ylabel("y")
ax9.set_xscale("linear")
ax9.set_yscale("linear")
matplotlib(fig9)

fig10, ax10 = plt.subplots()
y_err = 0.1 * np.random.rand(len(x))
ax10.errorbar(x, y_sin, yerr=y_err, label="sin", fmt="-o", color="blue")
ax10.errorbar(x, y_cos, yerr=y_err, label="cos", fmt="-x", color="red")
ax10.set_title("Errorbar Plot")
ax10.set_xlabel("x")
ax10.set_ylabel("y")
ax10.legend()
matplotlib(fig10)

fig11, ax11 = plt.subplots()
X, Y = np.meshgrid(np.arange(0, 10, 1), np.arange(0, 10, 1))
U = np.cos(X)
V = np.sin(Y)
ax11.quiver(X, Y, U, V)
ax11.set_title("Quiver Plot")
ax11.set_xlabel("x")
ax11.set_ylabel("y")
matplotlib(fig11)
