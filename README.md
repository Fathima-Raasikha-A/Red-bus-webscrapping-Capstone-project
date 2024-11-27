# Red Bus Web Scraping Application

This is a **Streamlit web application** designed to help users **effectively filter** the data wanted.
The application uses **web scraping** techniques to extract bus route information from the Red Bus website, 
  stores it in a MySQL database, and displays it in a user-friendly dashboard.

## Features

- **View Bus Routes**: The application scrapes bus route information, including route names and RTC (Road Transport Corporation) details.
- **Route Scraping**: By entering the URL of the website and specifying the number of pages to scrape, the app automatically fetches route details and displays them.
- **Database Integration**: The scraped data is stored in a **MySQL database**, making it easy to manage and access the data for further use.
- **Interactive Dashboard**: A **Streamlit dashboard** allows users to interact with the data, view various bus routes, and learn about different bus types and their corresponding RTCs.

## Libraries and Tools Used

- **Python**: The programming language used for building the application.
- **Pandas**: For data manipulation and creating DataFrames from the scraped data.
- **Selenium**: Used for automating web scraping of bus routes from the website.
- **Streamlit**: The framework used for building the interactive web app interface.
- **MySQL**: The relational database used to store the scraped data.
  
## How It Works

1. **URL Input**: You provide the URL of the website you want to scrape bus data from.
2. **Number of Pages**: You specify how many pages of bus routes you wish to scrape.
3. **Data Scraping**: The application uses **Selenium** to navigate the website and scrape bus route links and their corresponding names, along with RTC details.
4. **Data Storage**: The scraped data is stored in a **Pandas DataFrame**, which is then dumped into a **MySQL database**. This allows for easy access and management of the data.
5. **Dashboard**: A Streamlit-based **interactive dashboard** is created to display the data stored in the MySQL database, where users can explore bus routes and types.

## Error Handling and Challenges

While scraping the data, several common errors were encountered:

1. **Timeout Exceptions**: Occurred when a page took too long to load.
2. **No Such Element Exception**: Happened when the script tried to find an element that didn’t exist on the page.
3. **Stale Element Reference Exception**: This occurred when an element that was previously located is no longer attached to the DOM (Document Object Model).

I handled these exceptions by referring to **Selenium's official documentation**, experimenting with various error-handling techniques, 
and spending extra time debugging to ensure that the scraping process runs smoothly.

## Database Integration

- **MySQL Database**: After scraping the data, a **Pandas DataFrame** is created, which holds all the bus routes and related details. This DataFrame is then dumped into a MySQL database.
- **SQL Table Creation**: A table is created in the database to store the bus route information, making it easy to add, retrieve, and update data.
- **Dashboard**: The Streamlit app pulls the data from the MySQL database and presents it in an interactive dashboard, where users can explore bus routes,
    view details about each RTC, and check various bus types.
