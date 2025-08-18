# Instructions for Adding Contact Images

For Jarvis's vision-based WhatsApp feature to work, you need to provide a small screenshot of each contact's name as it appears in your WhatsApp chat list.

## How to Create a Contact Image:

1.  **Open WhatsApp Web or the Desktop App.**
2.  **Find your contact list** on the left-hand side.
3.  **Take a small, clean screenshot** of just the contact's name.
    *   **IMPORTANT:** Crop the image to include *only the name*. Do not include the profile picture, the last message, or the timestamp.
    *   The cleaner the image, the more reliably Jarvis can find it.
    *   Make sure the text is clear and not blurry.

4.  **Save the image** in this directory (`whatsapp_contact_images/`).
    *   The filename **must be the contact's name in lowercase**, with a `.png` extension.
    *   For example, if the contact is "Tillu", save the file as `tillu.png`.
    *   If the contact is "My Mom", save the file as `my mom.png`.

## Example:

If your contact list looks like this:

```
+------------------+
| 📸 Tillu         |
|   Hey there!     |
+------------------+
| 📸 John Doe      |
|   See you soon.  |
+------------------+
```

You would capture just the name "Tillu" and save it as `tillu.png`.

---

**Tip:** If Jarvis has trouble finding a contact, try taking a new screenshot. Lighting, screen resolution, and even dark/light mode can affect how the image looks. Consistency is key!
