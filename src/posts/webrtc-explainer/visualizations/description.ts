import { customElement, property } from "lit/decorators.js";
import { LitElement, type HTMLTemplateResult, html, css, type CSSResultGroup } from "lit";
@customElement("bb-webrtc-sdp-visualization")
export class WebRTCSDPVisualizationElement extends LitElement {
	@property()
	public sdp: string;

	public constructor() {
		super();
		this.description = "";
	}

	protected render(): HTMLTemplateResult {
		return html`
			<p>${this.description}</p>
		`;
	}
	public static styles?: CSSResultGroup = css`
		:host {
			display: flex;
			flex-direction: column;
			gap: 1rem;
		}
		#controls {
			display: flex;
			gap: .5rem;
			flex-wrap: wrap;
		}
		#candidates {
			display: flex;
			flex-direction: column;
		}
	`;
}
