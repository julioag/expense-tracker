// Test the enhanced Spanish bank parser
const sampleEmail = "Julio Andres Andrade Gomez: Te informamos que se ha realizado una compra por $71.000 con Tarjeta de Crédito ****5646 en EL BACO SANTIAGO CL el 19/07/2025 22:23. Revisa Saldos y Movimientos en App Mi";

// Mock the n8n input structure
const mockInput = {
    all: () => [{
        json: {
            body: sampleEmail
        }
    }]
};

// Simulate the n8n parser function
function parseSpanishEmail($input) {
    const emailContent = $input.all()[0].json.body || $input.all()[0].json.text || $input.all()[0].json;

    // Extract amount - pattern: "por $71.000"
    const amountMatch = emailContent.match(/por\s*\$([0-9.,]+)/i);
    let amount = null;
    if (amountMatch) {
        let amountStr = amountMatch[1].replace(/\./g, ''); // Remove dots (thousand separators)
        amount = parseFloat(amountStr);
    }

    // Extract merchant - pattern: "en [MERCHANT] el"
    const merchantMatch = emailContent.match(/en\s+([A-Z0-9\s\-\.]+?)\s+el\s+\d/i);
    let merchant = null;
    if (merchantMatch) {
        merchant = merchantMatch[1].trim()
            .toLowerCase()
            .split(' ')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }

    // Extract date - pattern: "el 19/07/2025 22:23"
    const dateMatch = emailContent.match(/el\s+(\d{1,2}\/\d{1,2}\/\d{4})\s+(\d{1,2}:\d{2})/i);
    let transaction_date = new Date().toISOString(); // fallback to now
    if (dateMatch) {
        const [day, month, year] = dateMatch[1].split('/');
        const time = dateMatch[2];
        transaction_date = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}T${time}:00`;
    }

    // Detect payment method from email content
    function detectPaymentMethod(content) {
        const contentLower = content.toLowerCase();
        
        // Credit card indicators in Spanish
        const creditIndicators = [
            'tarjeta de crédito',
            'credito',
            'compra',
            'cargo'
        ];
        
        // Debit card indicators in Spanish
        const debitIndicators = [
            'tarjeta de débito',
            'debito',
            'retiro',
            'cajero'
        ];
        
        // Transfer indicators in Spanish
        const transferIndicators = [
            'transferencia',
            'envío',
            'pago a',
            'envio'
        ];
        
        // Check for credit card
        if (creditIndicators.some(indicator => contentLower.includes(indicator))) {
            return 'credit_card';
        }
        
        // Check for transfers
        if (transferIndicators.some(indicator => contentLower.includes(indicator))) {
            return 'bank_transfer';
        }
        
        // Check for debit
        if (debitIndicators.some(indicator => contentLower.includes(indicator))) {
            return 'debit_card';
        }
        
        // Default to debit card
        return 'debit_card';
    }

    // Extract card last 4 digits - pattern: "****5646"
    function extractCardLastFour(content) {
        const cardMatch = content.match(/\*{4}[-\s]?(\d{4})/);
        return cardMatch ? cardMatch[1] : null;
    }

    // Determine payment method and card details
    const payment_method = detectPaymentMethod(emailContent);
    const card_last_four = extractCardLastFour(emailContent);

    // Return enhanced data for webhook
    return [{
        json: {
            amount: amount,
            merchant: merchant,
            description: `Purchase at ${merchant || 'Unknown'}`,
            transaction_date: transaction_date,
            source_email: "spanish_bank",
            raw_data: emailContent,
            payment_method: payment_method,
            card_last_four: card_last_four
        }
    }];
}

// Test the parser
console.log('=== Testing Enhanced Spanish Bank Parser ===');
console.log('Input email:', sampleEmail);
console.log('');

const result = parseSpanishEmail(mockInput);
console.log('Parsed result:', JSON.stringify(result[0].json, null, 2));

// Test the expected output
const expected = {
    amount: 71000,
    merchant: "El Baco Santiago Cl",
    payment_method: "credit_card",
    card_last_four: "5646",
    transaction_date: "2025-07-19T22:23:00"
};

console.log('');
console.log('=== Validation ===');
console.log('✅ Amount extracted:', result[0].json.amount === expected.amount);
console.log('✅ Merchant extracted:', result[0].json.merchant === expected.merchant);
console.log('✅ Payment method detected:', result[0].json.payment_method === expected.payment_method);
console.log('✅ Card last four extracted:', result[0].json.card_last_four === expected.card_last_four);
console.log('✅ Date extracted:', result[0].json.transaction_date === expected.transaction_date);

console.log('');
console.log('=== Billing Logic ===');
console.log('🏦 Payment Method:', result[0].json.payment_method);
if (result[0].json.payment_method === 'credit_card') {
    console.log('💳 This is a CREDIT CARD transaction');
    console.log('📅 Will affect budget on NEXT billing cycle (e.g., next month)');
    console.log('🔢 Card ending in:', result[0].json.card_last_four);
} else {
    console.log('🏧 This is a DEBIT/IMMEDIATE transaction');
    console.log('📅 Will affect budget IMMEDIATELY');
} 