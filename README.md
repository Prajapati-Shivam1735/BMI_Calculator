🩺 BMI Dashboard (Tkinter + MySQL + ttkbootstrap)

  A modern BMI (Body Mass Index) Dashboard built with Python, Tkinter, ttkbootstrap, MySQL, and Matplotlib.
  The app calculates BMI, stores entries in a MySQL database, analyzes user trends, visualizes them, and provides full record-management tools.

🚀 Features

✅ BMI Calculation
- Supports Metric (kg/m) and Imperial (lbs/in) units
- Automatically classifies BMI (Underweight, Normal, Overweight, Obesity)

💾 Database Integration (MySQL)

  - Saves all BMI records with:

    - username
    - weight
    - height
    - unit system
    - computed BMI
    - category
    - timestamp

📜 History Management

  - View all users' history (grouped)
  - View personal history
  - Delete selected records
  - Delete all records (with inline confirmation)
  - Search/filter in history (username, date, BMI)

📈 Analytics

  - Trend graph using Matplotlib
  - BMI Improving / Worsening / Stable” message displayed
  - Preview trend directly in the main window

🎨 Modern UI

  - Dark/Light theme toggle
  - Clean layout using ttkbootstrap (Cyborg / Flatly themes)
