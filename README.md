# Speech Pilot App

## Description:

This application combines two powerful functionalities in the world of audio: **converting text to audio data (BLOB)** and the ability to **test and play these sounds** directly from SQLite databases. Whether you're a developer needing to create dynamic audio files or a user wanting to explore stored audio content, this application provides you with the necessary tools.

**Key Features:**

*   **Text to Speech BLOB Conversion:**
    *   Select an SQLite database and the table containing the text to be converted.
    *   Specify the source text column and the destination column for storing the audio data (BLOB).
    *   Utilize the power of the `gTTS` library to convert text into high-quality audio files.
    *   Monitor the conversion process directly through the integrated progress bar.

*   **Dynamic Audio Playback and Testing:**
    *   Connect to SQLite databases and browse tables containing audio data (BLOB).
    *   Select the columns containing descriptive data (such as title or description) in addition to the audio column (BLOB).
    *   View the audio data alongside its descriptive information.
    *   Play stored sounds directly with a button click, thanks to the integration of the `pygame` library.

**How the App Works:**

1. **Conversion:** The application reads text from the database, converts it to audio data using `gTTS`, and then stores this data as a BLOB in the table you specify.
2. **Testing:** The application allows you to browse the audio data stored in the database and play it directly, enabling you to verify the quality of the generated sounds or explore existing audio content.

**Get Started Now!**

[Add here the detailed "Getting Started" section you mentioned previously, with installation and running steps.]

**Built With:**

[Add here the "Built With" section you mentioned previously.]

**Contributing:**

[Add here the "Contributing" section you mentioned previously.]

**License:**

[Add here the "License" section you mentioned previously.]

**Example of a portion of the "Getting Started" section:**

```markdown
## Getting Started:

1. **Ensure Python and Requirements are Installed:**
   ```bash
   pip install tkinter ttkbootstrap pygame gTTS