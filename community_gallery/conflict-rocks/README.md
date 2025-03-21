# Conflict Rocks - Example With VPS Hosting

This example is live at:

https://conflict.rocks/

or

https://conflict-rocks-229753-yqqemgiy-ndjz2ws6la-ue.a.run.app/

## Dataset Source

This project visualizes data on diamond mining locations and conflicts funded by diamond trade. The datasets used are:

- **Mines Dataset** (`mines_csv`): Contains latitude and longitude of global diamond mines.
- **War-Related Deaths Dataset** (`deaths_csv`): Contains details about conflicts where rebel groups were funded by diamond sales.

## What This App Does

This app maps diamond mining activity and correlates it with conflicts funded by diamond trade. The main features include:

1. **Interactive Map**: Displays global diamond mining locations with zoom functionality.
2. **Conflict Data Visualization**: Shows war-related deaths in conflicts where diamonds were a major funding source.

## How to Run Locally

### Prerequisites

Ensure you have:
- **Python** installed
- **Docker** installed
- **Preswald** installed (`pip install preswald`)

### Running the App Locally

1. Clone the repository:
   
  `git clone https://github.com/StructuredLabs/preswald.git`

2. Go to this example:
   
  `cd examples/conflict-rocks`
   
2. Start the app:
   
  `preswald run`

3. If not done automatically, open your browser and go to:
   
  `http://localhost:8501`

## How to deploy to VPS

If you are a fan of self hosting, I included a script that you could use to deploy your Preswald app to a VPS with a custom domain.


Ensure you have:
- **SSH Agent Forwarding** configured
- **DNS Records** pointing to your VPS IP
- **Docker** installed locally

### Deploy the App to Your VPS

1. Set VPS_PUBLIC_IP variable in deploy.sh

   ```bash
   #!/bin/bash

   VPS_PUBLIC_IP=<YOUR.VPS.PUBLIC.IP>
   ```
   
    to:
   
   ```bash
   #!/bin/bash

   VPS_PUBLIC_IP=123.456.78.91
   ```

2. Set DOMAIN_NAME and EMAIL variables in vps_entry.sh

   ```bash
   #!/bin/bash

   DOMAIN_NAME=<YOUR-DOMAiN.TLD>
   EMAIL=<YOUR-EMAIL>
   ```
   
    to:
   
   ```bash
   #!/bin/bash

   DOMAIN_NAME=customdomain.com
   EMAIL=definitelymyemail@gmail.com
   ```
3. Run deploy.sh inside your project directory

   `
   bash deploy.sh
   `
