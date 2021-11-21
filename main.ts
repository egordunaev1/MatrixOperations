import { App, Editor, MarkdownView, Modal, Notice, Plugin, PluginSettingTab, Setting, Vault, FileSystemAdapter } from 'obsidian';
import { PythonShell } from 'python-shell';


interface MatrixOperationsSettings {
	pythonPath: string;
	commands: string;
}

const DEFAULT_SETTINGS: MatrixOperationsSettings = {
	pythonPath: '',
	commands: ''
}

export default class MatrixOperationsPlugin extends Plugin {
	settings: MatrixOperationsSettings;
	pyshell: PythonShell;
	id: 1;
	editors: {};

	run_pyshell() {
		// Getting vault path
		var path = ""
		if (this.app.vault.adapter instanceof FileSystemAdapter) {
			path = this.app.vault.adapter.getBasePath();
		}

		// Setting up python shell
		let pyshell_options = {
			mode: 'json',
			parser: function (x: any) {
				try {
					return JSON.parse(x);
				} catch (e) {
					return JSON.stringify({ command: 'null' });
				}
			},
			pythonPath: this.settings.pythonPath,
			scriptPath: path + "/.obsidian/plugins/MatrixOperations/src/",
			args: [this.settings.commands]
		};

		this.pyshell = new PythonShell('main.py', pyshell_options);

		this.id = 1;
		this.editors = {};

		this.pyshell.on('message', (message: object) => {
			if (message.command) {
				let editor = this.editors[message.id];
				switch (message.command) {
					case 'simplify': editor.replaceSelection(message.res); break;
					case 'el_ops': editor.replaceSelection(message.res); break;
					case 'transpose': editor.replaceSelection(message.res); break;
					case 'inverse': editor.replaceSelection(message.res); break;
					case 'ref': editor.replaceSelection(message.res); break;
					case 'rref': editor.replaceSelection(message.res); break;
					case 'matrix_info': new TextModal(this.app, message.res).open(); break;
					case 'error': new Notice(message.res); break;
				}
				delete this.editors[message.id];
			}
		});

		// Setting up commands
		this.addCommand({
			id: 'simplify',
			name: 'simplify',
			editorCallback: (editor: Editor, view: MarkdownView) => {
				this.editors[this.id] = editor;
				let latex = editor.getSelection();
				this.pyshell.send({ command: 'simplify', text: latex, 'id': this.id });
				this.id++;
			}
		});

		this.addCommand({
			id: 'el_ops',
			name: 'el_ops',
			editorCallback: (editor: Editor, view: MarkdownView) => {
				this.editors[this.id] = editor;
				let latex = editor.getSelection();
				this.pyshell.send({ command: 'el_ops', text: latex, 'id': this.id });
				this.id++;
			}
		});

		this.addCommand({
			id: 'matrix_info',
			name: 'matrix_info',
			editorCallback: (editor: Editor, view: MarkdownView) => {
				this.editors[this.id] = editor;
				let latex = editor.getSelection();
				this.pyshell.send({ command: 'matrix_info', text: latex, 'id': this.id });
				this.id++;
			}
		});

		this.addCommand({
			id: 'inverse_matrix',
			name: 'inverse_matrix',
			editorCallback: (editor: Editor, view: MarkdownView) => {
				this.editors[this.id] = editor;
				let latex = editor.getSelection();
				this.pyshell.send({ command: 'inverse', text: latex, 'id': this.id });
				this.id++;
			}
		});

		this.addCommand({
			id: 'transpose_matrix',
			name: 'transpose_matrix',
			editorCallback: (editor: Editor, view: MarkdownView) => {
				this.editors[this.id] = editor;
				let latex = editor.getSelection();
				this.pyshell.send({ command: 'transpose', text: latex, 'id': this.id });
				this.id++;
			}
		});

		this.addCommand({
			id: 'ref',
			name: 'ref',
			editorCallback: (editor: Editor, view: MarkdownView) => {
				this.editors[this.id] = editor;
				let latex = editor.getSelection();
				this.pyshell.send({ command: 'ref', text: latex, 'id': this.id });
				this.id++;
			}
		});

		this.addCommand({
			id: 'rref',
			name: 'rref',
			editorCallback: (editor: Editor, view: MarkdownView) => {
				this.editors[id] = editor;
				let latex = editor.getSelection();
				this.pyshell.send({ command: 'rref', text: latex, 'id': this.id });
				this.id++;
			}
		});
	}

	async onload() {
		await this.loadSettings();
		this.addSettingTab(new SettingTab(this.app, this));
		this.run_pyshell();
	}

	onunload() {
		this.pyshell.kill();
	}

	async loadSettings() {
		this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
	}

	async saveSettings() {
		await this.saveData(this.settings);
	}
}

class TextModal extends Modal {
	message = "";

	constructor(app: App, message: string) {
		super(app);
		this.message = message;
	}

	onOpen() {
		const { contentEl } = this;
		contentEl.setText(this.message);
	}

	onClose() {
		const { contentEl } = this;
		contentEl.empty();
	}
}


class SettingTab extends PluginSettingTab {
	plugin: MatrixOperationsPlugin;

	constructor(app: App, plugin: MatrixOperationsPlugin) {
		super(app, plugin);
		this.plugin = plugin;
	}

	display(): void {
		const { containerEl } = this;

		containerEl.empty();

		containerEl.createEl('h2', { text: 'Matrix Calculator - Settings' });

		new Setting(containerEl)
			.setName('Python path')
			.setDesc('Path to your python3 file with required packages (see README.md)')
			.addText(text => text
				.setPlaceholder('path')
				.setValue(this.plugin.settings.pythonPath)
				.onChange(async (value) => {
					this.plugin.settings.pythonPath = value;
					await this.plugin.saveSettings();
					this.plugin.pyshell.kill();
					this.plugin.run_pyshell();
				}));

		new Setting(containerEl)
			.setName('Command file')
			.setDesc('Path to file with your custom LaTeX commands (\\newcommand)')
			.addText(text => text
				.setPlaceholder('path')
				.setValue(this.plugin.settings.commands)
				.onChange(async (value) => {
					this.plugin.settings.commands = value;
					await this.plugin.saveSettings();
					this.plugin.pyshell.kill();
					this.plugin.run_pyshell();
				}));
	}
}
