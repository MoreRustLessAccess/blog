import { customElement, state, property } from "lit/decorators.js";
import { map } from "lit/directives/map.js";
import { LitElement, type HTMLTemplateResult, html, css, type CSSResultGroup } from "lit";
@customElement("bb-webrtc-ice-candidates-visualization")
export class WebRTCIceCandidatesVisualizationElement extends LitElement {
	@property({type: Array})
	public controls: string[];
	@property({type: Number})
	public durationMultiplier: number;
	
	// State
	@state()
	private candidates: RTCIceCandidate;

	public constructor() {
		super();
		this.controls = [];
		this.durationMultiplier = 1;
		this.candidates = [];
	}

	protected render(): HTMLTemplateResult {
		return html`
			<div id="controls">
				<button @click=${async () => {
					this.candidates = [];

					const abortController = new AbortController();

					const connection = new RTCPeerConnection();
					const startTime = Date.now();

					connection.addEventListener("icecandidate", async (event) => {
						const candidate = event.candidate;
						if (candidate === null) {
							abortController.abort();
							return;
						}
						const duration = Date.now() - startTime;
						const timeToSleep = duration * (this.durationMultiplier - 1);
						console.log({timeToSleep, duration});
						await new Promise(resolve => setTimeout(resolve, timeToSleep));
						this.candidates = [...this.candidates, candidate];
					}, {signal: abortController.signal});
					abortController.signal.addEventListener("abort", () => {
						connection.close();
					});

					await connection.createDataChannel("test", {});

					const offer = await connection.createOffer();
					await connection.setLocalDescription(offer);
				}}>Fetch</button>
				<div class="field" ?hidden=${this.controls.includes("durationMultiplier")}>
					<label for="duration-multiplier">Duration multiplier</label>
					<input
						id="duration-multiplier"
						type="range"
						min="1"
						max="100"
						value="1"
						required
						@input=${(event: Event) => {
							const input = event.target as HTMLInputElement;
							this.durationMultiplier = parseFloat(input.value);
						}}
					>
					<output>${this.durationMultiplier}</output>
				</div>
			</div>
			<div id="candidates">
				${map(this.candidates, candidate => html`
					<span class="candidate">${candidate.candidate}</span>
			  `)}
			</div>
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
