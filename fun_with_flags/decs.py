import functools

from flask import flash, redirect, session, url_for



def error_check(view):
	@functools.wraps(view)
	def wrapped_view(**kwargs):
		error = None

		try:
			view(**kwargs)

		except:
			error = f"Something went wrong on page '{view.__name__}'. \
								Please try again or report an error to joschobart on hattrick.org."

		if error is not None:
			flash(error)

			return redirect(url_for('index'))

		return view(**kwargs)

	return wrapped_view



def login_required(view):
	@functools.wraps(view)
	def wrapped_view(**kwargs):
		username = session.get('username')

		if not username:

			return redirect(url_for('auth.authorize'))


		return view(**kwargs)

	return wrapped_view
