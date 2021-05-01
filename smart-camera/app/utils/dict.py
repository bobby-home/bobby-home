def remove_null_keys(d):
   return {
      k:v
      for k, v in d.items()
      if v is not None
   }

