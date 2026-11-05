const path = require('node:path');

function argumentValue(args, name) {
    for(let index = args.length - 1; index >= 0; index--){
        if(args[index].startsWith(`${name}=`)){
            return args[index].slice(name.length + 1);
        }
        if(args[index] === name){
            return args[index + 1];
        }
    }
    return undefined;
}

function instanceOptions(argv, defaultApp = false) {
    const ignored = new Set(['--no-sandbox', '--ozone-platform-hint=auto']);
    const args = argv.slice(defaultApp ? 2 : 1).filter((arg) => !ignored.has(arg));
    const portValue = argumentValue(args, '--port');
    const port = portValue === undefined ? 9337 : Number(portValue);
    if(!Number.isInteger(port) || port < 1 || port > 65535){
        throw new Error('Crosstalk --port must be an integer between 1 and 65535');
    }
    const storageDir = argumentValue(args, '--storage-dir');
    return {
        args,
        port,
        backendOrigin: `http://localhost:${port}`,
        userData: storageDir ? path.join(path.resolve(storageDir), 'desktop') : null,
        label: storageDir ? path.basename(path.resolve(storageDir)) : null,
    };
}

module.exports = { instanceOptions };
