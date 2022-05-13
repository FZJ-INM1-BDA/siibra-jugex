<svelte:window on:message={handleMessage}/>

{#if !destroyFlag}
<Card>
	<Content>
		<h3>ROI Selection</h3>
		<RoiSelection
			on:RoiSelected={ev => handleUpdateParam({ roi_1: ev.detail })}
			label="Select ROI 1"
			postMessage={postMessage}/>
		<RoiSelection
			on:RoiSelected={ev => handleUpdateParam({ roi_2: ev.detail })}
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
		<JugexSlider min={100} max={10000} step={1} value={defaultPerm} on:ValueUpdated={ev => handleUpdateParam({ permutations: ev.detail })} />
	</Content>
</Card>

<div class="spacer"></div>

<Card>
	<Content>
		<h3>Threshold</h3>
		<JugexSlider min={0} max={1} step={0.01} value={defaultTreshold} on:ValueUpdated={ev => handleUpdateParam({ threshold: ev.detail })} />
	</Content>
</Card>

<div class="spacer"></div>

<Card>
	<Content>
		<Group>
			<Button on:click={runAnalysis} disabled={!canRunFlag}>
				<Label>
					Run
				</Label>
			</Button>

			{#if canRunFlag}
			<Button href={notebookUrl} target="_blank" disabled={!canRunFlag}>
				<Label>
					Notebook
				</Label>
			</Button>
			{:else}
			<Button disabled>
				<Label>
					Notebook
				</Label>
			</Button>
			{/if}
		</Group>
		{#if runningFlag}
		<CircularProgress style="width:1rem;height:1rem;" indeterminate />
		{/if}

		{#if errorText}
		{errorText}
		{/if}

		{#if downloadUrl || result}
		<hr>
		{/if}

		{#if result}
		<DataTable>
			<Head>
				<Row>
					<Cell>gene</Cell>
					<Cell>p-value</Cell>
				</Row>
			</Head>
			<Body>
				{#each Object.entries(result['result']['p-values']) as [gene, pval]}
				<Row>
					<Cell>{gene}</Cell>
					<Cell>{pval}</Cell>
				</Row>
				{/each}
			</Body>
		</DataTable>
		{/if}

		{#if downloadUrl}
		<Button href={downloadUrl} download="result.json">
			<Icon class="material-icons">file_download</Icon>
			<Label>
				Save
			</Label>
		</Button>
		{/if}

		{#if result && hasDataSrcFlag}
		<ShowResult {postMessage} {result} />
		{/if}

	</Content>
</Card>
{/if}

<script>
	import RoiSelection from "./RoiSelection.svelte"
	import GeneSelection from "./GeneSelection.svelte"
	import JugexSlider from "./JugexSlider.svelte"
	import { hasDataSrc, getGeneNames, SIIBRA_JUGEX_ENDPOINT, parcellationId } from "./store.js"
	import Card, { Content } from "@smui/card"
	import Button, { Label, Icon, Group } from "@smui/button"
	import CircularProgress from "@smui/circular-progress"
	import ShowResult from "./ShowResult.svelte"
  	import { onDestroy, tick } from "svelte"
	import DataTable, { Head, Body, Row, Cell } from "@smui/data-table"

	const getUuid = () => crypto.getRandomValues(new Uint32Array(1))[0].toString(16)

	let destroyFlag = false
	let destroyCbObj = []

	let hasDataSrcFlag = false
	let src = undefined
	let runningFlag = false
	let canRunFlag = false
	let srcOrigin = undefined
	let errorText = undefined
	let downloadUrl = undefined
	let genes = []
	let result = undefined

	const defaultPerm = 100
	const defaultTreshold = 0.2
	let notebookUrl = ""

	let param = {
		parcellation_id: parcellationId,
		permutations: defaultPerm,
		threshold: defaultTreshold,
		roi_1: null,
		roi_2: null,
		genes: [],
	}

	$: canRunFlag = !runningFlag && !!param.roi_1 && !!param.roi_2 && param.genes.length > 0
	$: {
		const searchParam = new URLSearchParams()
		searchParam.set("parcellation_id", parcellationId)
		searchParam.set("roi_1", param.roi_1)
		searchParam.set("roi_2", param.roi_2)
		searchParam.set("comma_delimited_genes", param.genes.join(","))
		searchParam.set("permutations", param.permutations)
		searchParam.set("threshold", param.threshold)
		
		notebookUrl = `../notebook/view?${searchParam.toString()}`
	}

	hasDataSrc.subscribe(flag => hasDataSrcFlag = flag)

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
			break
		}
	}

  onDestroy(async () => {
    destroyFlag = true
    await tick()
		src.postMessage({
			method: `sxplr.exit`,
      params: {
        requests: destroyCbObj
      },
			jsonrpc: '2.0',
      id: getUuid()
		}, srcOrigin)
  })

	async function postMessage(_msg) {
    if (destroyFlag) {
      destroyCbObj = [...destroyCbObj, {..._msg, id: getUuid() }]
      return
    }
		const id = getUuid()
		const { abortSignal, ...msg } = _msg
		if (abortSignal) {
			abortSignal.onAbort(() => {
				src.postMessage({
					method: `sxplr.cancelRequest`,
					jsonrpc: '2.0',
					params: { id },
				}, srcOrigin)
			})
		}
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
		result = null
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

			result = await new Promise((rs, rj) => {
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
						rj("operation failed")
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