#!/usr/bin/env python3
"""Auditable Responses API transport, separated from write orchestration.
No API key or raw authorization headers are written to disk.
"""
from __future__ import annotations
import json, os, urllib.error, urllib.request, urllib.parse
from dataclasses import dataclass

API_URL="https://api.openai.com/v1/responses"

class ModelError(Exception): pass
class MissingCredential(ModelError): pass
class ModelProtocolError(ModelError): pass

@dataclass(frozen=True)
class ModelResult:
    response_id: str
    model: str
    text: str
    usage: dict
    provider_kind: str


def parse_response(data: dict, provider_kind="openai_live") -> ModelResult:
    if data.get('status') not in (None,'completed'):
        raise ModelProtocolError('Response not completed; no output accepted')
    if data.get('error'):
        raise ModelProtocolError('Response contains error')
    texts=[]
    for item in data.get('output') or []:
        if item.get('type')=='message':
            for part in item.get('content') or []:
                if part.get('type')=='output_text' and isinstance(part.get('text'),str):
                    texts.append(part['text'])
    t=''.join(texts).strip()
    if not t:
        raise ModelProtocolError('Empty text output; do not assume output[0] is text')
    rid=data.get('id')
    if not isinstance(rid,str) or not rid.strip():
        raise ModelProtocolError('Response identity missing')
    return ModelResult(rid,data.get('model','UNKNOWN_MODEL'),t,data.get('usage') or {},provider_kind)

class OpenAIResponses:
    def __init__(self,model,api_key=None,endpoint=API_URL,timeout=120,allow_loopback_test=False):
        self.api_key=api_key if api_key is not None else os.environ.get('OPENAI_API_KEY')
        self.model=model
        self.endpoint=endpoint
        self.timeout=timeout
        self.allow_loopback_test=allow_loopback_test
        u=urllib.parse.urlparse(endpoint)
        is_official=(u.scheme=='https' and u.netloc=='api.openai.com' and u.path=='/v1/responses')
        is_local=(allow_loopback_test and u.scheme=='http' and u.hostname in ('127.0.0.1','localhost')
                  and u.path=='/v1/responses')
        if not (is_official or is_local):
            raise ModelProtocolError('Endpoint is not official TLS endpoint or explicitly enabled test loopback')
        self.provider_kind='local_protocol_fixture' if is_local else 'openai_live'
        self.last_transport={}

    def generate(self, instructions, prompt, max_output_tokens=6000) -> ModelResult:
        self.last_transport={}
        if not self.api_key:
            raise MissingCredential('OPENAI_API_KEY is absent; LIVE_MODEL_UNVERIFIED')
        if not self.model:
            raise ModelProtocolError('Model name must be explicitly configured')
        body=json.dumps({'model':self.model,'instructions':instructions,'input':prompt,
                          'max_output_tokens':max_output_tokens,'store':False},ensure_ascii=False).encode('utf-8')
        req=urllib.request.Request(self.endpoint,data=body,
              headers={'Authorization':'Bearer '+self.api_key,'Content-Type':'application/json'},method='POST')
        try:
            with urllib.request.urlopen(req,timeout=self.timeout) as res:
                if res.status != 200: raise ModelProtocolError('HTTP status '+str(res.status))
                raw=res.read(8_000_000+1)
                if len(raw)>8_000_000:raise ModelProtocolError('Response exceeds 8MB cap')
        except urllib.error.HTTPError as e:
            # Do not echo raw response bodies which may reflect private content.
            raise ModelError('Provider HTTP status '+str(e.code)) from None
        except urllib.error.URLError:
            raise ModelError('Provider transport failed; no response identity available') from None
        try: data=json.loads(raw)
        except (UnicodeDecodeError,json.JSONDecodeError) as e:raise ModelProtocolError('Malformed provider JSON') from e
        # Auditable payload only: never authorization headers or credentials.
        self.last_transport={'provider_response':data,'provider_status':data.get('status')}
        return parse_response(data,self.provider_kind)
