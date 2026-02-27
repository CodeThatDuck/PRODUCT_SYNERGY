/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'ibm-blue': '#0062ff',
        'ibm-blue-hover': '#0050e6',
        'ibm-blue-light': '#e0f0ff',
        'ibm-gray-10': '#f4f4f4',
        'ibm-gray-20': '#e0e0e0',
        'ibm-gray-50': '#8d8d8d',
        'ibm-gray-70': '#525252',
        'ibm-gray-100': '#161616',
        'ibm-green': '#24a148',
        'ibm-yellow': '#f1c21b',
        'ibm-red': '#da1e28',
      },
      borderWidth: {
        '3': '3px',
      },
      fontFamily: {
        'ibm': ['IBM Plex Sans', 'sans-serif'],
      },
    },
  },
  plugins: [],
}

// Made with Bob
