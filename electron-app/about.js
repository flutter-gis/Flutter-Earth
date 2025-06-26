document.addEventListener('DOMContentLoaded', async () => {
    // --- DOM Elements ---
    const greetingTextElement = document.getElementById('greetingText');
    const versionTextElement = document.getElementById('versionText'); // Assuming it might become dynamic
    const visitWebsiteButton = document.getElementById('visitWebsiteButton');
    const changelogTextArea = document.getElementById('changelogTextArea');

    const nameDialogModal = document.getElementById('nameDialogModal');
    const nameField = document.getElementById('nameField');
    const saveNameButton = document.getElementById('saveNameButton');
    const closeNameDialogButton = document.getElementById('closeNameDialog');

    let userName = '';
    let namePrompted = false; // To match QML logic of prompting once if name not set

    // --- Helper Functions ---
    function updateGreeting() {
        // In QML, ThemeProvider.getCatchphrase was used.
        // For Electron, we'll simplify or assume these phrases are hardcoded or fetched differently.
        if (userName) {
            greetingTextElement.textContent = `Hello ${userName}!`;
        } else {
            greetingTextElement.textContent = "Hello!";
        }
    }

    function openNameDialog() {
        nameDialogModal.style.display = 'block';
    }

    function closeNameDialog() {
        nameDialogModal.style.display = 'none';
    }

    // --- Load Initial Data ---
    async function loadAboutData() {
        if (!window.electronAPI || !window.electronAPI.invokePython) {
            console.error("electronAPI or invokePython is not available. Check preload script and main process setup.");
            greetingTextElement.textContent = "Error: Backend connection failed.";
            changelogTextArea.value = "Could not load changelog.";
            return;
        }

        try {
            // Fetch user_name
            const fetchedUserName = await window.electronAPI.invokePython('get-setting', 'user_name');
            userName = fetchedUserName || ''; // QML used backend.getSetting("user_name") || ""
                                            // invokePython for get-setting should return the value or null/undefined

            // Fetch changelog
            const changelog = await window.electronAPI.invokePython('get-changelog');
            changelogTextArea.value = changelog || "Changelog not available.";

            updateGreeting();

            // Logic to prompt for name (matches QML's Component.onCompleted)
            // We need a way to persist 'namePrompted' if we want it to behave exactly like QML
            // (prompt only once per session if name isn't set).
            // For simplicity, we'll prompt if name is not set.
            // A more accurate simulation would involve checking a session flag.
            if (!userName && !sessionStorage.getItem('nameDialogPromptedThisSession')) {
                openNameDialog();
                sessionStorage.setItem('nameDialogPromptedThisSession', 'true'); // Mark as prompted for this session
            }

        } catch (error) {
            console.error("Error loading about data:", error);
            greetingTextElement.textContent = "Error loading data.";
            changelogTextArea.value = "Error loading changelog.";
        }
    }

    // --- Event Listeners ---
    if (visitWebsiteButton) {
        visitWebsiteButton.addEventListener('click', () => {
            if (window.electronAPI && window.electronAPI.invokePython) {
                // In Electron, opening external URL is usually done in the main process for security.
                // We'll need an IPC call for this.
                window.electronAPI.invokePython('open-external-url', 'https://github.com/jakobnewman/Flutter-Earth');
            } else {
                // Fallback for environments where electronAPI might not be fully set up (e.g. simple browser)
                window.open('https://github.com/jakobnewman/Flutter-Earth', '_blank');
            }
        });
    }

    if (saveNameButton) {
        saveNameButton.addEventListener('click', async () => {
            const newName = nameField.value.trim();
            if (newName.length > 0) {
                try {
                    await window.electronAPI.invokePython('set-setting', 'user_name', newName);
                    userName = newName;
                    updateGreeting();
                    closeNameDialog();
                } catch (error) {
                    console.error("Error saving user name:", error);
                    alert("Failed to save name. See console for details.");
                }
            } else {
                alert("Name cannot be empty.");
            }
        });
    }

    if (closeNameDialogButton) {
        closeNameDialogButton.addEventListener('click', closeNameDialog);
    }

    // Close modal if user clicks outside of the modal content
    window.addEventListener('click', (event) => {
        if (event.target === nameDialogModal) {
            closeNameDialog();
        }
    });

    // Initial load
    await loadAboutData();
});

console.log('About script (about.js) loaded.');
