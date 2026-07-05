import { exec } from 'child_process';
import path from 'path';

export async function parsePdf(args: { pdfPath: string }): Promise<any> {
  return new Promise((resolve, reject) => {
    // In CommonJS, __dirname is available globally.
    // TypeScript might complain if it thinks it's ESM, but since target is NodeNext and package.json is commonjs,
    // __dirname is the correct way.
    const scriptPath = path.resolve(__dirname, '../../parse_pdf.py');
    
    // We know the exact working python executable path on this system
    const pythonPaths = [
      'python',
      'C:\\Users\\cd250\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe'
    ];
    
    let currentPathIndex = 0;
    
    function tryExecute() {
      const pythonCmd = pythonPaths[currentPathIndex];
      const cmd = `"${pythonCmd}" "${scriptPath}" "${args.pdfPath}"`;
      
      exec(cmd, (error, stdout, stderr) => {
        if (error) {
          // If the simple 'python' command failed, try the next one (which is the hardcoded python core path)
          if (currentPathIndex < pythonPaths.length - 1) {
            currentPathIndex++;
            tryExecute();
            return;
          }
          reject(new Error(`Failed to execute PDF parser: ${error.message}. Stderr: ${stderr}`));
          return;
        }
        
        try {
          const parsed = JSON.parse(stdout);
          if (parsed.error) {
            reject(new Error(parsed.error));
          } else {
            resolve(parsed);
          }
        } catch (e: any) {
          reject(new Error(`Failed to parse script output: ${stdout}. Error: ${e.message}`));
        }
      });
    }
    
    tryExecute();
  });
}
