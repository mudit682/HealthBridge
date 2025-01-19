// Import required modules
const express = require('express');
const mongoose = require('mongoose');
const bodyParser = require('body-parser');

// Initialize Express app
const app = express();
app.use(bodyParser.json()); // Middleware to parse JSON requests

// Connect to MongoDB
mongoose.connect('mongodb://localhost:27017/gnid_sapp', {
    useNewUrlParser: true,
    useUnifiedTopology: true,
});

const db = mongoose.connection;
db.on('error', console.error.bind(console, 'connection error:'));
db.once('open', () => {
    console.log('Connected to MongoDB');
});

// Define a schema for hospital resources
const resourceSchema = new mongoose.Schema({
    hospitalName: { type: String, required: true },
    resourceType: { type: String, required: true }, // e.g., Beds, Oxygen, Ventilators
    quantity: { type: Number, required: true },
    lastUpdated: { type: Date, default: Date.now },
});

// Create a model from the schema
const Resource = mongoose.model('Resource', resourceSchema);

// Route to add or update resources
app.post('/addResource', async (req, res) => {
    const { hospitalName, resourceType, quantity } = req.body;

    if (!hospitalName || !resourceType || quantity === undefined) {
        return res.status(400).json({ message: 'All fields are required: hospitalName, resourceType, and quantity.' });
    }

    try {
        // Check if the resource already exists for the hospital
        const existingResource = await Resource.findOne({ hospitalName, resourceType });

        if (existingResource) {
            // Update the existing resource
            existingResource.quantity = quantity;
            existingResource.lastUpdated = Date.now();
            await existingResource.save();
            return res.status(200).json({ message: 'Resource updated successfully', resource: existingResource });
        } else {
            // Create a new resource
            const newResource = new Resource({ hospitalName, resourceType, quantity });
            await newResource.save();
            return res.status(201).json({ message: 'Resource added successfully', resource: newResource });
        }
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Internal Server Error' });
    }
});

// Start the server
const PORT = 5000;
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});