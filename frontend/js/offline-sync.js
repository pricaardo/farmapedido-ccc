function salvarRascunhoOffline(pedidoData) {
    const request = indexedDB.open("FarmaPedidoDB", 1);
    
    request.onsuccess = function(event) {
        const db = event.target.result;
        const transaction = db.transaction(["rascunhos"], "readwrite");
        const store = transaction.objectStore("rascunhos");
        store.add(pedidoData);
        console.log("Rascunho salvo. Será enviado quando a conexão voltar.");
    };
}