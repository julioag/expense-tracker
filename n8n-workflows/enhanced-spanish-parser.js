// Enhanced n8n Function Node - Spanish Bank Email Parser with Payment Method Detection
// Input: $input.all()[0].json (email content)

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
            return 'CREDIT_CARD';
        }
        
        // Check for transfers
        if (transferIndicators.some(indicator => contentLower.includes(indicator))) {
            return 'BANK_TRANSFER';
        }
        
        // Check for debit
        if (debitIndicators.some(indicator => contentLower.includes(indicator))) {
            return 'DEBIT_CARD';
        }
        
        // Default to debit card
        return 'DEBIT_CARD';
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