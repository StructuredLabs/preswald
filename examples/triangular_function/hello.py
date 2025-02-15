from preswald import matplotlib
import numpy as np

x = np.linspace(0, 50, 100)
sin = np.sin(x)
cos = np.cos(x)
tan = np.tan(x)

plt = matplotlib.plt
plt.figure(figsize=(10, 6))

plt.plot(x, sin, 'b--', label='sin(x)', linewidth=2)
plt.plot(x, cos, 'r--', label='cos(x)', linewidth=2)
plt.plot(x, tan, 'g--', label='tan(x)', linewidth=2)

plt.title('Sinus Waves', fontsize=16, pad=20)

plt.xlabel('X axis', fontsize=12)
plt.ylabel('Y axis', fontsize=12)

plt.legend(loc='upper right', fontsize=10)

plt.grid(True, linestyle='--', alpha=0.5)

plt.xlim(0, 10)
plt.ylim(-1.5, 1.5)

matplotlib(plt.gcf(), format='svg')