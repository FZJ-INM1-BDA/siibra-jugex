<svelte:window on:message={handleMessage}/>

<Card>
	<Content>
		<h3>ROI Selection</h3>
		<RoiSelection
			on:RoiSelected={ev => handleUpdateParam({ roi_1: ev.detail })}
			regions={regions}
			label="Select ROI 1"
			postMessage={postMessage}/>
		<RoiSelection
		on:RoiSelected={ev => handleUpdateParam({ roi_2: ev.detail })}
			regions={regions}
			label="Select ROI 2"
			postMessage={postMessage}/>
	</Content>	
</Card>

<div class="spacer"></div>

<Card>
	<Content>
		<h3>Genes selection</h3>
		<GeneSelection on:GeneSelected={ev => handleUpdateParam({ genes: ev.detail })} genes={genes} />
	</Content>
</Card>

<div class="spacer"></div>

<Card>
	<Content>
		<h3>Permutations</h3>
		<Permutation on:PermutationUpdated={ev => handleUpdateParam({ permutations: ev.detail })} />
	</Content>
</Card>

<div class="spacer"></div>

<Card>
	<Content>
		<Button on:click={runAnalysis} disabled={runningFlag}>
			<Label>
				Run
			</Label>
		</Button>
		{#if runningFlag}
		<CircularProgress style="width:1rem;height:1rem;" indeterminate />
		{/if}

		{#if downloadUrl}
		<Button href={downloadUrl} download="result.json">
			<Icon class="material-icons">file_download</Icon>
			<Label>
				Save
			</Label>
		</Button>
		{/if}
		{#if errorText}
		{errorText}
		{/if}
	</Content>
</Card>
<script>
	import RoiSelection from "./RoiSelection.svelte"
	import GeneSelection from "./GeneSelection.svelte"
	import Permutation from "./Permutation.svelte"
	import { hasDataSrc, getGeneNames, SIIBRA_JUGEX_ENDPOINT, parcellationId } from "./store.js"
	import Card, { Content } from "@smui/card"
	import Button, { Label, Icon } from "@smui/button"
	import CircularProgress from "@smui/circular-progress"

	const getUuid = () => crypto.getRandomValues(new Uint32Array(1))[0].toString(16)

	let regions = []
	let src = undefined
	let runningFlag = false
	let srcOrigin = undefined
	let errorText = undefined
	let downloadUrl = undefined
	let genes = []

	let param = {
		parcellation_id: parcellationId,
		permutations: 1000
	}
	function handleUpdateParam(newParam){
		param = {
			...param,
			...newParam,
		}
	}

	getGeneNames().then(({ genes:_genes }) => {
		genes = _genes
	})
	
	const requestMap = new Map()

	function handleMessage(msg) {
		const { source, data, origin } = msg
		const { id, method, params, result, error } = data
		if (!!result || !!error ) {
			if (!id) {
				throw new Error(`expecting result/error to have id`)
			}
			if (!requestMap.has(id)) {
				throw new Error(`expecting requestMap to have id ${id}, but it does not.`)
			}
			
			const { rs, rj } = requestMap.get(id)
			requestMap.delete(id)

			if (result) return rs(result)
			if (error) return rj(error)
		}
		if (!/^sxplr/.test(method)) return
		switch (method) {
			case 'sxplr.init': {
				hasDataSrc.update(() => true)
				source.postMessage({
					id,
					jsonrpc: '2.0',
					result: {
						name: 'siibra-jugex'
					}
				}, origin)
				src = source
				srcOrigin = origin
				break
			}
			case 'sxplr.on.allRegions': {
				regions = params.filter(r => r.hasAnnotation && r.hasAnnotation.internalIdentifier)
			}
			break
		}
	}

	async function postMessage(_msg) {
		const id = getUuid()
		const { abortSignal, ...msg } = _msg
		abortSignal.onAbort(() => {
			src.postMessage({
				method: `sxplr.cancelRequest`,
				jsonrpc: '2.0',
				params: { id },
			}, srcOrigin)
		})
		src.postMessage({
			...msg,
			id,
			jsonrpc: '2.0',
		}, srcOrigin)
		return new Promise((rs, rj) => {
			requestMap.set(id, { rs, rj })
		})
	}

	async function runAnalysis(){
		if (runningFlag) {
			console.warn(`analysis already running, do not start a new one`)
			return
		}
		runningFlag = true
		errorText = null
		if (downloadUrl) {
			URL.revokeObjectURL(downloadUrl)
			downloadUrl = null
		}

		try {
			const res = await fetch(`${SIIBRA_JUGEX_ENDPOINT}/analysis/analysis`, {
				method: 'POST',
				body: JSON.stringify(param),
				headers: {
					'content-type': 'application/json'
				}
			})
			if (res.status >= 400) {
				throw new Error(res.statusText)
			}
			const { poll_url } = await res.json()

			const result = await new Promise((rs, rj) => {
				const intervalRef = setInterval(async () => {
					const res = await fetch(`${SIIBRA_JUGEX_ENDPOINT}/analysis/analysis/${poll_url}`)
					if (res.status >= 400) {
						return rj(res.statusText)
					}
					const { status, result } = await res.json()
					if (status === "SUCCESS") {
						console.log('SUCCESS', result)
						clearInterval(intervalRef)
						rs(result)
					}
					if (status === "FAILURE") {
						console.log('FAILURE')
						clearInterval(intervalRef)
						rj("operation feailed")
					}
				}, 1000)
			})

			const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'text/plain' })
			downloadUrl = URL.createObjectURL(blob)
		} catch (e) {
			errorText = e.toString()
		} finally {
			runningFlag = false
		}
	}

</script>

<style>
	div.spacer
	{
		height:1rem;
	}
</style>