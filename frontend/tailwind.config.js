/** @type {import('tailwindcss').Config} */
import typography from "@tailwindcss/typography";

export default {
	darkMode: ["class"],
	content: [
		"./index.html", // Include index.html
		"./src/**/*.{js,jsx}", // Include all JS and JSX files in src
	],
	theme: {
		extend: {
			typography: {
				//Custom styles for compatibility with various themes
				DEFAULT: {
					css: {
						'--tw-prose-body': 'hsl(var(--foreground))',
						'--tw-prose-headings': 'hsl(var(--foreground))',
						'--tw-prose-lead': 'hsl(var(--foreground))',
						'--tw-prose-links': 'hsl(var(--foreground))',
						'--tw-prose-bold': 'hsl(var(--foreground))',
						'--tw-prose-counters': 'hsl(var(--foreground))',
						'--tw-prose-bullets': 'hsl(var(--foreground))',
						'--tw-prose-hr': 'hsl(var(--foreground))',
						'--tw-prose-quotes': 'hsl(var(--foreground))',
						'--tw-prose-quote-borders': 'hsl(var(--foreground))',
						'--tw-prose-captions': 'hsl(var(--foreground))',
						'--tw-prose-code': 'hsl(var(--foreground))',
						'--tw-prose-pre-code': 'hsl(var(--foreground))',
						'--tw-prose-pre-bg': 'hsl(var(--foreground))',
						'--tw-prose-th-borders': 'hsl(var(--foreground))',
						'--tw-prose-td-borders': 'hsl(var(--foreground))',
						'--tw-prose-invert-body': 'hsl(var(--foreground))',
						'--tw-prose-invert-headings': 'hsl(var(--foreground))',
						'--tw-prose-invert-lead': 'hsl(var(--foreground))',
						'--tw-prose-invert-links': 'hsl(var(--foreground))',
						'--tw-prose-invert-bold': 'hsl(var(--foreground))',
						'--tw-prose-invert-counters': 'hsl(var(--foreground))',
						'--tw-prose-invert-bullets': 'hsl(var(--foreground))',
						'--tw-prose-invert-hr': 'hsl(var(--foreground))',
						'--tw-prose-invert-quotes': 'hsl(var(--foreground))',
						'--tw-prose-invert-quote-borders': 'hsl(var(--foreground))',
						'--tw-prose-invert-captions': 'hsl(var(--foreground))',
						'--tw-prose-invert-code': 'hsl(var(--foreground))',
						'--tw-prose-invert-pre-code': 'hsl(var(--foreground))',
						'--tw-prose-invert-pre-bg': 'hsl(var(--foreground))',
						'--tw-prose-invert-th-borders': 'hsl(var(--foreground))',
						'--tw-prose-invert-td-borders': 'hsl(var(--foreground))',
					}
				}
			},
			borderRadius: {
				lg: 'var(--radius)',
				md: 'calc(var(--radius) - 2px)',
				sm: 'calc(var(--radius) - 4px)'
				},
				colors: {
					background: 'hsl(var(--background))',
					foreground: 'hsl(var(--foreground))',
					card: {
						DEFAULT: 'hsl(var(--card))',
						foreground: 'hsl(var(--card-foreground))'
					},
					popover: {
						DEFAULT: 'hsl(var(--popover))',
						foreground: 'hsl(var(--popover-foreground))'
					},
					primary: {
						DEFAULT: 'hsl(var(--primary))',
						foreground: 'hsl(var(--primary-foreground))'
					},
					secondary: {
						DEFAULT: 'hsl(var(--secondary))',
						foreground: 'hsl(var(--secondary-foreground))'
					},
					muted: {
						DEFAULT: 'hsl(var(--muted))',
						foreground: 'hsl(var(--muted-foreground))'
					},
					accent: {
						DEFAULT: 'hsl(var(--accent))',
						foreground: 'hsl(var(--accent-foreground))'
					},
					destructive: {
						DEFAULT: 'hsl(var(--destructive))',
						foreground: 'hsl(var(--destructive-foreground))'
					},
					border: 'hsl(var(--border))',
					input: 'hsl(var(--input))',
					ring: 'hsl(var(--ring))',
					chart: {
						'1': 'hsl(var(--chart-1))',
						'2': 'hsl(var(--chart-2))',
						'3': 'hsl(var(--chart-3))',
						'4': 'hsl(var(--chart-4))',
						'5': 'hsl(var(--chart-5))'
					},
					sidebar: {
						DEFAULT: 'hsl(var(--sidebar-background))',
						foreground: 'hsl(var(--sidebar-foreground))',
						primary: 'hsl(var(--sidebar-primary))',
						'primary-foreground': 'hsl(var(--sidebar-primary-foreground))',
						accent: 'hsl(var(--sidebar-accent))',
						'accent-foreground': 'hsl(var(--sidebar-accent-foreground))',
						border: 'hsl(var(--sidebar-border))',
						ring: 'hsl(var(--sidebar-ring))'
					}
				},
				keyframes: {
					"accordion-down": {
						from: { height: 0 },
						to: { height: "var(--radix-accordion-content-height)" },
					},
					"accordion-up": {
						from: { height: "var(--radix-accordion-content-height)" },
						to: { height: 0 },
					},
					"slide-from-left": {
						"0%": { transform: "translateX(-100%)" },
						"100%": { transform: "translateX(0)" },
					},
					"slide-to-left": {
						"0%": { transform: "translateX(0)" },
						"100%": { transform: "translateX(-100%)" },
					},
				},
				animation: {
					"accordion-down": "accordion-down 0.2s ease-out",
					"accordion-up": "accordion-up 0.2s ease-out",
					"slide-from-left": "slide-from-left 0.3s ease-out",
					"slide-to-left": "slide-to-left 0.3s ease-in",
				},
			}
		},
		plugins: [typography, require("tailwindcss-animate")],
	};
