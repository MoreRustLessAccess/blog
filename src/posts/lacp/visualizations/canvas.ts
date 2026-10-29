import { css, html, LitElement, type CSSResultGroup, type HTMLTemplateResult } from "lit";
import { customElement, property } from "lit/decorators.js";

@customElement("bb-lacp-canvas")
export class LACPCanvasElement extends LitElement {
	@property({type: Number})
	public height: number;
	@property({type: Number})
	public width: number;

	public constructor() {
		super();
		
		// This just follows the canvas element's default size
		this.height = 150;
		this.width = 300;
	}

	protected render(): HTMLTemplateResult {
	    return html`
			<canvas height=${this.height} width=${this.width}></canvas>
		`;
	}
	public static styles?: CSSResultGroup = css`
		canvas {
			height: 100%;
			width: 100%;
		}
	`;
}
